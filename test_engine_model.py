from unittest import TestCase

import numpy as np

from engine import System, Domain, Matrix
from engine_model import _sorted_products, _sorted_substances
from lca_model import Product
from lca_model_fixture import *


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

    def test_multiply__should_raise_when_incompatible_domains(self):
        key1, product1 = ('database', 'version' 'product 1'), Product('product 1', Quantity(1.0, kg), 1)
        key2, product2 = ('database', 'version' 'product 2'), Product('product 2', Quantity(5.0, kg), 1)

        domain1 = Domain({key1: 1}, {key1: product1})
        matrix1 = Matrix(domain1, domain1, np.array([]))

        domain2 = Domain({key2: 2}, {key1: product1, key2: product2})
        matrix2 = Matrix(domain2, domain2, np.array([]))

        with self.assertRaises(ValueError):
            matrix1 * matrix2


class TestSystem(TestCase):

    @staticmethod
    def expected_activity_domain(database):
        return {
            (*database.key, 'A'): 0,
            (*database.key, 'B'): 1,
            (*database.key, 'B2'): 2,
            (*database.key, 'C'): 3,
            (*database.key, 'D'): 4,
            (*database.key, 'E'): 5
        }

    def test_technosphere_domain(self):
        database = complex_database()
        matrix = System(database).technosphere_matrix

        self.assertEqual(matrix.input_domain, matrix.output_domain)
        self.assertEqual(matrix.input_domain._indices, self.expected_activity_domain(database))

    def test_technosphere_array(self):
        database = complex_database()
        matrix = System(database).technosphere_matrix

        self.assertFalse((matrix.array - np.array([
            [3.6e6, 0, 0, 0, 0, 0],
            [-4 * 3.6e6 * 0.75, 1, 0, 0, 0, 0],
            [-4 * 3.6e6 * 0.25, 0, 1, 0, 0, 0],
            [-3.6e6, -200, 0, 4e3, 0, 0],
            [-3.6e6, -2e3, 0, 0, 3.6e9 / 2, 0],
            [-3.6e9, 0, 0, 0, 0, 1]
        ])).any())

    def test_biosphere_domain(self):
        database = complex_database()
        matrix = System(database).biosphere_matrix

        self.assertEqual(matrix.input_domain._indices, self.expected_activity_domain(database))
        self.assertEqual(matrix.output_domain._indices, {
            (database.name, database.version, 'S1'): 0,
            (database.name, database.version, 'S2'): 1,
            (database.name, database.version, 'S3'): 2,
        })

    def test_biosphere_array(self):
        database = complex_database()
        matrix = System(database).biosphere_matrix

        self.assertEqual(matrix.array.shape, (6, 3))
        self.assertFalse((matrix.array - np.array([
            [0.2, 0, 0],
            [0.1 * 0.75, 0, 0],
            [0.1 * 0.25, 0, 0],
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 1e-3],  # allocation
        ])).any())


class TestFunctions(TestCase):
    def test_sorted_activities(self):
        database = complex_realistic_database()
        self.assertEqual([p.name for p in _sorted_products(database)], [
            'electricity',
            'fertiliser',
            'land transformation',
            'phosphate, at mine',
            'wheat grain',
            'wheat straw',
        ])

    def test_sorted_substances(self):
        database = complex_realistic_database()
        self.assertEqual([s.name for s in _sorted_substances(database)], [
            'carbon dioxide',
            'dinitrogen monoxide',
            'water',
        ])
