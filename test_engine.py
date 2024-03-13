from unittest import TestCase

import numpy as np
from quantities import Quantity, kg

import model_fixture
from engine import LcaSystem, Domain, Matrix, OperatorChain, _Operator, _OperatorValidator
from model import Product, Database
from test_utils import almost_equal


def expected_activity_domain(database):
    return {
        (*database.key, 'electricity'): 0,
        (*database.key, 'fertiliser'): 1,
        (*database.key, 'land transformation'): 2,
        (*database.key, 'phosphate, at mine'): 3,
        (*database.key, 'wheat grain'): 4,
        (*database.key, 'wheat straw'): 5
    }


class TestDomain(TestCase):

    def test_indexed_elements(self):
        database = Database('name', '1.0', [])

        product1 = Product('product 1', Quantity(1.0, kg), 0.9)
        product2 = Product('product 2', Quantity(3.0, kg), 1.0)

        key1 = (*database.key, product1.name)
        key2 = (*database.key, product2.name)

        domain = Domain({key1: 1, key2: 2},
                        {key1: product1, key2: product2})

        self.assertEqual(domain.indexed_elements, [(1, product1), (2, product2)])


class TestMatrix(TestCase):
    database = Database('name', '1.0', [])

    product1 = Product('product 1', Quantity(1.0, kg), 0.9)
    product2 = Product('product 2', Quantity(3.0, kg), 1.0)
    product3 = Product('product 3', Quantity(5.0, kg), 2.0)

    key1 = (*database.key, product1.name)
    key2 = (*database.key, product2.name)
    key3 = (*database.key, product2.name)

    domain1 = Domain({key1: 1, key2: 2},
                     {key1: product1, key2: product2})

    domain2 = Domain({key1: 1, key2: 2, key3: 3},
                     {key1: product1, key2: product2, key3: product3})

    def test_multiply__should_have_correct_domains(self):
        a = Matrix(self.domain1, self.domain1, np.array([
            [1.0, 2.0],
            [3.0, 0.5]
        ]))

        b = Matrix(self.domain1, self.domain2, np.array([
            [4.0, 2.0],
            [1.0, 2.0]
        ]))

        c = a * b

        self.assertEqual(c.input_domain, self.domain1)
        self.assertEqual(c.output_domain, self.domain2)

    def test_multiply__should_have_correct_array(self):
        a = Matrix(self.domain1, self.domain1, np.array([
            [1.0, 2.0],
            [3.0, 0.5]
        ]))

        b = Matrix(self.domain1, self.domain2, np.array([
            [4.0, 2.0],
            [1.0, 2.0]
        ]))

        c = a * b

        self.assertFalse((c.array - np.dot(a.array, b.array)).any())


class TestLcaSystem(TestCase):

    def test_technosphere_matrix__should_have_correct_domains(self):
        database = model_fixture.database()
        matrix = LcaSystem(database).technosphere_matrix

        self.assertEqual(matrix.input_domain, matrix.output_domain)
        self.assertEqual(matrix.input_domain._indices, expected_activity_domain(database))

    def test_technosphere_matrix__should_have_correct_array(self):
        database = model_fixture.database()
        matrix = LcaSystem(database).technosphere_matrix

        self.assertFalse((matrix.array - np.array([
            [3.6e9, 0, 0, 0, 0, 0],
            [-0.2 * 3.6e6, 1, 0, -2, 0, 0],
            [0, 0, 1e4, 0, 0, 0],
            [-0.1 * 3.6e6, 0, 0, 1, 0, 0],
            [0, -10 * 0.6, -500 * 1e4 * 0.6, 0, 1170, 0],  # cycle, allocation
            [0, -10 * 0.4, -500 * 1e4 * 0.4, 0, -50 * 0.4, 300],  # allocation
        ])).any())

    def test_biosphere_matrix__should_have_correct_domains(self):
        database = model_fixture.database()
        matrix = LcaSystem(database).biosphere_matrix

        self.assertEqual(matrix.input_domain._indices, expected_activity_domain(database))
        self.assertEqual(matrix.output_domain._indices, {
            (database.name, database.version, 'carbon dioxide'): 0,
            (database.name, database.version, 'dinitrogen monoxide'): 1,
            (database.name, database.version, 'water'): 2,
        })

    def test_biosphere_matrix__should_have_correct_array(self):
        database = model_fixture.database()
        matrix = LcaSystem(database).biosphere_matrix

        self.assertEqual(matrix.array.shape, (6, 3))
        self.assertFalse((matrix.array - np.array([
            [5, 0, 0],
            [0, 0, 0],
            [6, 0, 0],
            [2, 0, 0],
            [100 * 0.6, 5 * 0.6, 1500 * 0.6],  # allocation
            [100 * 0.4, 5 * 0.4, 1500 * 0.4],  # allocation
        ])).any())


class _OperatorValidatorTest(TestCase):

    def test_validate__when_compatible_operators__then_ok(self):
        key1, product1 = ('database', 'version' 'product 1'), Product('product 1', Quantity(1.0, kg), 1)
        key2, product2 = ('database', 'version' 'product 2'), Product('product 2', Quantity(5.0, kg), 1)

        domain1 = Domain({key1: 1, key2: 2}, {key1: product1, key2: product2})
        operator1 = _Operator(domain1, domain1)

        try:
            _OperatorValidator.validate(operator1, operator1)
        except ValueError:
            self.fail('should not raise exception')

    def test_validate__when_incompatible_operators__then_exception(self):
        key1, product1 = ('database', 'version' 'product 1'), Product('product 1', Quantity(1.0, kg), 1)
        key2, product2 = ('database', 'version' 'product 2'), Product('product 2', Quantity(5.0, kg), 1)

        domain1 = Domain({key1: 1}, {key1: product1})
        operator1 = _Operator(domain1, domain1)

        domain2 = Domain({key2: 2}, {key1: product1, key2: product2})
        operator2 = _Operator(domain2, domain2)

        with self.assertRaises(ValueError):
            _OperatorValidator.validate(operator1, operator2)


class TestOperatorChain(TestCase):

    def test_solve__when_supply__should_have_correct_domains(self):
        system = LcaSystem(model_fixture.supply_database_fixture())
        matrix = OperatorChain(system).supply().solve()

        self.assertEqual(matrix.input_domain, system.technosphere_matrix.input_domain)
        self.assertEqual(matrix.output_domain, system.technosphere_matrix.output_domain)

    #      A    B    C    D    E
    # A    1    0    0    0    0
    # B   -1    1    0    0    0
    # C   -1   -200  4    0    0
    # D   -1    0   -2   0.5   0
    # E   -1000 0    0    0    1
    def test_solve__when_supply__should_have_correct_array(self):
        system = LcaSystem(model_fixture.supply_database_fixture())
        matrix = OperatorChain(system).supply().solve()
        self.assertTrue(almost_equal(matrix.array, np.array([
            [0, 0, 0, 0, 0],
            [7.2e6, 0, 0, 0, 0],
            [360900, 0.05, 0, 0, 0],
            [2 * (2000 * 7.2e6 + 3.6e6) / 3.6e9, 2 * 2000 / 3.6e9, 0, 1, 0],
            [3.6e9, 0, 0, 0, 0],
        ])))
