from unittest import TestCase

import numpy as np
from quantities import Quantity, kg

import model_fixture
from engine import System, Domain, OperatorChain, _Operator, _OperatorValidator
from model import Product
from test_utils import almost_equal


class OperatorValidatorTest(TestCase):

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


class TestOperationDomain(TestCase):

    def test_supply(self):
        database = model_fixture.complex_database()
        system = System(database)
        matrix = OperatorChain(system).supply().solve()

        self.assertEqual(matrix.input_domain, system.technosphere_matrix.input_domain)
        self.assertEqual(matrix.output_domain, system.technosphere_matrix.output_domain)

    def test_inventory(self):
        system = System(model_fixture.complex_database())
        matrix = OperatorChain(system).inventory().solve()

        self.assertEqual(matrix.input_domain, system.biosphere_matrix.input_domain)
        self.assertEqual(matrix.output_domain, system.biosphere_matrix.output_domain)


class TestSystemWithUnitConversion(TestCase):

    def test_biosphere(self):
        database = model_fixture.simple_database_with_unit_conversions()
        system = System(database)
        matrix = system.biosphere_matrix.array
        self.assertTrue(almost_equal(matrix, np.array([
            [5],
            [0.5]
        ])))

    def test_technosphere(self):
        database = model_fixture.simple_database_with_unit_conversions()
        system = System(database)
        matrix = system.technosphere_matrix.array
        self.assertTrue(almost_equal(matrix, np.array([
            [500, -2],
            [0, 1]
        ])))

    def test_supply(self):
        database = model_fixture.simple_database_with_unit_conversions()
        system = System(database)
        matrix = OperatorChain(system).supply().solve().array
        self.assertTrue(almost_equal(matrix, np.array([
            [0, 2 / 500],
            [0, 0]
        ])))

    def test_inventory(self):
        database = model_fixture.simple_database_with_unit_conversions()
        system = System(database)
        matrix = OperatorChain(system).inventory().solve().array
        self.assertTrue(almost_equal(matrix, np.array([
            [(5 + 2 * 0.5) / 500],
            [0.5]
        ])))


class TestSystemWithAllocation(TestCase):

    def test_biosphere(self):
        database = model_fixture.simple_database_with_allocation()
        system = System(database)
        matrix = system.biosphere_matrix.array
        self.assertTrue(almost_equal(matrix, np.array([
            [5 * 0.5],
            [0.5]
        ])))

    def test_technosphere(self):
        database = model_fixture.simple_database_with_allocation()
        system = System(database)
        matrix = system.technosphere_matrix.array
        self.assertTrue(almost_equal(matrix, np.array([
            [500, -1],
            [0, 1]
        ])))

    def test_supply(self):
        database = model_fixture.simple_database_with_allocation()
        system = System(database)
        matrix = OperatorChain(system).supply().solve().array
        self.assertTrue(almost_equal(matrix, np.array([
            [0, 2 / 500 * 0.5],
            [0, 0]
        ])))

    def test_inventory(self):
        database = model_fixture.simple_database_with_allocation()
        system = System(database)
        matrix = OperatorChain(system).inventory().solve().array
        self.assertTrue(almost_equal(matrix, np.array([
            [(5 + 2 * 0.5) / 500 * 0.5],
            [0.5]
        ])))


class TestSystemWithCycle(TestCase):

    def test_biosphere(self):
        database = model_fixture.simple_database_with_cycle()
        system = System(database)
        matrix = system.biosphere_matrix.array
        self.assertTrue(almost_equal(matrix, np.array([
            [5],
            [0.5]
        ])))

    def test_technosphere(self):
        database = model_fixture.simple_database_with_cycle()
        system = System(database)
        matrix = system.technosphere_matrix.array
        self.assertTrue(almost_equal(matrix, np.array([
            [400, -2],
            [0, 1]
        ])))

    def test_supply(self):
        database = model_fixture.simple_database_with_cycle()
        system = System(database)
        matrix = OperatorChain(system).supply().solve().array
        self.assertTrue(almost_equal(matrix, np.array([
            [0, 2 / 400],
            [0, 0]
        ])))

    def test_inventory(self):
        database = model_fixture.simple_database_with_cycle()
        system = System(database)
        matrix = OperatorChain(system).inventory().solve().array
        self.assertTrue(almost_equal(matrix, np.array([
            [(5 + 2 * 0.5) / 400],
            [0.5]
        ])))


class TestComplexSystem(TestCase):

    def test_supply(self):
        system = System(model_fixture.complex_database())
        matrix = OperatorChain(system).supply().solve()
        amt_of_a_for_b = 4 * 3.6e6 * .75
        real_amt_d = 3.6e9 * 0.5
        self.assertTrue(almost_equal(matrix.array, np.array([
            [0, 0, 0, 0, 0, 0],
            [amt_of_a_for_b, 0, 0, 0, 0, 0],
            [4 * 3.6e6 * .25, 0, 0, 0, 0, 0],
            [(amt_of_a_for_b * 200 + 3.6e6) / 4e3, 200 / 4e3, 0, 0, 0, 0],
            [(2e3 * amt_of_a_for_b + 3.6e6) / real_amt_d, 2e3 / real_amt_d, 0, 0, 1, 0],
            [3.6e9, 0, 0, 0, 0, 0],
        ])))

    def test_inventory(self):
        system = System(model_fixture.complex_database())
        matrix = OperatorChain(system).inventory().solve()
        s1_amt_for_b = (4 * 0.2 + .1) * .75
        self.assertTrue(almost_equal(matrix.array, np.array([
            [.2 / 3.6e6, 0, 0],
            [s1_amt_for_b, 0, 0],
            [(4 * 0.2 + .1) * .25, 0, 0],
            [(s1_amt_for_b * 200 + .2) / 4e3, 0, 0],
            [0, 0, 0],
            [0.2 * 1e3, 0, 1e-3],
        ])))
