from unittest import TestCase

from quantities import Quantity, kg

import model_fixture
from model import Product, Substance


class TestProduct(TestCase):

    def test_hashable(self):
        product = Product('product', Quantity(1.0, kg), 1.0)
        self.assertEqual({product, product}, {product})

    def test_equal(self):
        self.assertEqual(Product('product', Quantity(1.0, kg), 1.0),
                         Product('product', Quantity(1.0, kg), 1.0))

    def test_equal__when_same_hash_but_different_type(self):
        substance = Substance('name')
        product = Product('name', Quantity(1.0, kg), 1.0)
        self.assertEqual(hash(substance), hash(product))
        self.assertNotEqual(product, substance)


class TestSubstance(TestCase):

    def test_hashable(self):
        substance = Substance('water')
        self.assertEqual({substance, substance}, {substance})

    def test_equal(self):
        self.assertEqual(Substance('water'), Substance('water'))


class TestDatabase(TestCase):

    def test_key(self):
        database = model_fixture.complex_realistic_database()
        self.assertEqual(database.key, (database.name, database.version))

    def test_sorted_activities(self):
        database = model_fixture.complex_realistic_database()
        self.assertEqual([p.name for p in database.sorted_products()], [
            'electricity',
            'fertiliser',
            'land transformation',
            'phosphate, at mine',
            'wheat grain',
            'wheat straw',
        ])

    def test_sorted_substances(self):
        database = model_fixture.complex_realistic_database()
        self.assertEqual([s.name for s in database.sorted_substances()], [
            'carbon dioxide',
            'dinitrogen monoxide',
            'water',
        ])
