from quantities import Quantity, kg, m, ha, kWh, MWh, metric_ton

from model import Database
from parser import parse


def database_as_dict() -> dict:
    return {
        ('database', '1.0'): [
            {
                'name': 'wheat',
                'exchanges': [
                    {
                        'name': 'wheat grain',
                        'type': 'production',
                        'quantity': Quantity(1.2, metric_ton),
                        'allocation': 0.6
                    },
                    {
                        'name': 'wheat straw',
                        'type': 'production',
                        'quantity': Quantity(300, kg),
                        'allocation': 0.4
                    },
                    {
                        'name': 'wheat grain',
                        'type': 'technosphere',
                        'quantity': Quantity(50, kg)
                    },
                    {
                        'name': 'land transformation',
                        'type': 'technosphere',
                        'quantity': Quantity(500, ha)
                    },
                    {
                        'name': 'fertiliser',
                        'type': 'technosphere',
                        'quantity': Quantity(10, kg)
                    },
                    {
                        'name': 'water',
                        'type': 'biosphere',
                        'quantity': Quantity(1500, m ** 3)
                    },
                    {
                        'name': 'carbon dioxide',
                        'type': 'emission',
                        'quantity': Quantity(0.1, metric_ton)
                    },
                    {
                        'name': 'dinitrogen monoxide',
                        'type': 'emission',
                        'quantity': Quantity(5, kg)
                    }
                ]
            },
            {
                'name': 'land transformation',
                'exchanges': [
                    {
                        'name': 'land transformation',
                        'type': 'production',
                        'quantity': Quantity(1, ha),
                        'allocation': 1
                    },
                    {
                        'name': 'carbon dioxide',
                        'type': 'emission',
                        'quantity': Quantity(6, kg)
                    }
                ]
            },
            {
                'name': 'fertiliser',
                'exchanges': [
                    {
                        'name': 'fertiliser',
                        'type': 'production',
                        'quantity': Quantity(1, kg),
                        'allocation': 1
                    },
                    {
                        'name': 'electricity',
                        'type': 'technosphere',
                        'quantity': Quantity(0.2, kWh)
                    },
                    {
                        'name': 'phosphate, at mine',
                        'type': 'technosphere',
                        'quantity': Quantity(2, kg)
                    }
                ]
            },
            {
                'name': 'phosphate, at mine',
                'exchanges': [
                    {
                        'name': 'phosphate, at mine',
                        'type': 'production',
                        'quantity': Quantity(1, kg),
                        'allocation': 1
                    },
                    {
                        'name': 'electricity',
                        'type': 'technosphere',
                        'quantity': Quantity(0.1, kWh)
                    },
                    {
                        'name': 'carbon dioxide',
                        'type': 'emission',
                        'quantity': Quantity(2, kg)
                    }
                ]
            },
            {
                'name': 'electricity',
                'exchanges': [
                    {
                        'name': 'electricity',
                        'type': 'production',
                        'quantity': Quantity(1, MWh),
                        'allocation': 1
                    },
                    {
                        'name': 'carbon dioxide',
                        'type': 'emission',
                        'quantity': Quantity(5, kg)
                    }
                ]
            }
        ]
    }


def database() -> Database:
    return parse(database_as_dict())
