from unittest import TestCase

from lca_model import ExchangeType
from lca_model_fixture import *
from parser import DatabaseParser


class TestParser(TestCase):

    def test_parse__should_parse_name(self):
        database = DatabaseParser.parse(database_as_dict())
        self.assertEqual(database.name, 'database')

    def test_parse__should_parse_version(self):
        database = DatabaseParser.parse(database_as_dict())
        self.assertEqual(database.version, '1.0')

    def test_parse__should_parse_activities(self):
        database = DatabaseParser.parse(database_as_dict())
        self.assertEqual(len(database.activities), 5)

    def test_parse__when_wheat__should_parse_name(self):
        database = DatabaseParser.parse(database_as_dict())
        activity = database.activities[0]
        self.assertEqual(activity.name, 'wheat')

    def test_parse__when_wheat__should_parse_products(self):
        database = DatabaseParser.parse(database_as_dict())
        activity = database.activities[0]
        self.assertEqual(len(activity.production), 2)

        product1, product2 = activity.production
        self.assertEqual(product1.name, 'wheat grain')
        self.assertEqual(product1.quantity, Quantity(1.2, metric_ton))
        self.assertEqual(product1.allocation, 0.6)
        self.assertEqual(product2.name, 'wheat straw')
        self.assertEqual(product2.quantity, Quantity(300, kg))
        self.assertEqual(product2.allocation, 0.4)

    def test_parse__when_wheat__should_parse_technosphere(self):
        database = DatabaseParser.parse(database_as_dict())
        activity = database.activities[0]
        self.assertEqual(len(activity.technosphere), 3)

        exchange1, exchange2, exchange3 = activity.technosphere
        self.assertEqual(exchange1.name, 'wheat grain')
        self.assertEqual(exchange1.quantity, Quantity(50, kg))
        self.assertEqual(exchange2.name, 'land transformation')
        self.assertEqual(exchange2.quantity, Quantity(500, ha))
        self.assertEqual(exchange3.name, 'fertiliser')
        self.assertEqual(exchange3.quantity, Quantity(10, kg))

    def test_parse__when_wheat__should_parse_biosphere(self):
        database = DatabaseParser.parse(database_as_dict())
        activity = database.activities[0]
        self.assertEqual(len(activity.biosphere), 3)

        exchange1, exchange2, exchange3 = activity.biosphere
        self.assertEqual(exchange1.name, 'water')
        self.assertEqual(exchange1.type, ExchangeType.BIOSPHERE)
        self.assertEqual(exchange1.quantity, Quantity(1500, m ** 3))
        self.assertEqual(exchange2.name, 'carbon dioxide')
        self.assertEqual(exchange2.type, ExchangeType.EMISSION)
        self.assertEqual(exchange2.quantity, Quantity(0.1, metric_ton))
        self.assertEqual(exchange3.name, 'dinitrogen monoxide')
        self.assertEqual(exchange3.type, ExchangeType.EMISSION)
        self.assertEqual(exchange3.quantity, Quantity(5, kg))
