from unittest import TestCase

from lca_model import Product
from lca_model_fixture import *


class TestProduct(TestCase):

    def test_hashable(self):
        product = Product('product', Quantity(1.0, kg), 1.0, ())
        self.assertEqual({product, product}, {product})

    def test_equal(self):
        self.assertEqual(Product('product', Quantity(1.0, kg), 1.0, ()),
                         Product('product', Quantity(1.0, kg), 1.0, ()))

    def test_equal__when_different_database(self):
        self.assertNotEqual(Product('product', Quantity(1.0, kg), 1.0, ('database', '1')),
                            Product('product', Quantity(1.0, kg), 1.0, ('database', '2')))

    def test_equal__when_same_hash_but_different_type(self):
        substance = Substance('name')
        product = Product('name', Quantity(1.0, kg), 1.0, ())
        self.assertEqual(hash(substance), hash('name'))
        self.assertNotEqual(product, substance)


class TestSubstance(TestCase):

    def test_hashable(self):
        substance = Substance('water')
        self.assertEqual({substance, substance}, {substance})

    def test_equal(self):
        self.assertEqual(Substance('water'), Substance('water'))


class TestDatabase(TestCase):

    def test_key(self):
        database = complex_realistic_database()
        self.assertEqual(database.key, (database.name, database.version))
