from quantities import Quantity, kg, m, ha, kWh, MWh, metric_ton, g, litre

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


def simple_database_with_unit_conversions() -> Database:
    return parse({
        ('database', 'version'): [
            {
                'name': 'A',
                'exchanges': [
                    {
                        'name': 'A',
                        'type': 'production',
                        'quantity': Quantity(0.5, metric_ton),
                        'allocation': 1
                    },
                    {
                        'name': 'B',
                        'type': 'technosphere',
                        'quantity': Quantity(2, kg),
                    },
                    {
                        'name': 'carbon dioxide',
                        'type': 'emission',
                        'quantity': Quantity(5, kg)
                    }
                ]
            },
            {
                'name': 'B',
                'exchanges': [
                    {
                        'name': 'B',
                        'type': 'production',
                        'quantity': Quantity(1, kg),
                        'allocation': 1
                    },
                    {
                        'name': 'carbon dioxide',
                        'type': 'emission',
                        'quantity': Quantity(500, g)
                    }
                ]
            },
        ]
    })


def simple_database_with_allocation() -> Database:
    return parse({
        ('database', 'version'): [
            {
                'name': 'A',
                'exchanges': [
                    {
                        'name': 'A',
                        'type': 'production',
                        'quantity': Quantity(0.5, metric_ton),
                        'allocation': 0.5
                    },
                    {
                        'name': 'B',
                        'type': 'technosphere',
                        'quantity': Quantity(2, kg),
                    },
                    {
                        'name': 'carbon dioxide',
                        'type': 'emission',
                        'quantity': Quantity(5, kg)
                    }
                ]
            },
            {
                'name': 'B',
                'exchanges': [
                    {
                        'name': 'B',
                        'type': 'production',
                        'quantity': Quantity(1, kg),
                        'allocation': 1
                    },
                    {
                        'name': 'carbon dioxide',
                        'type': 'emission',
                        'quantity': Quantity(500, g)
                    }
                ]
            },
        ]
    })


def simple_database_with_cycle() -> Database:
    return parse({
        ('database', 'version'): [
            {
                'name': 'A',
                'exchanges': [
                    {
                        'name': 'A',
                        'type': 'production',
                        'quantity': Quantity(0.5, metric_ton),
                        'allocation': 1
                    },
                    {
                        'name': 'A',
                        'type': 'technosphere',
                        'quantity': Quantity(100, kg),
                    },
                    {
                        'name': 'B',
                        'type': 'technosphere',
                        'quantity': Quantity(2, kg),
                    },
                    {
                        'name': 'carbon dioxide',
                        'type': 'emission',
                        'quantity': Quantity(5, kg)
                    }
                ]
            },
            {
                'name': 'B',
                'exchanges': [
                    {
                        'name': 'B',
                        'type': 'production',
                        'quantity': Quantity(1, kg),
                        'allocation': 1
                    },
                    {
                        'name': 'carbon dioxide',
                        'type': 'emission',
                        'quantity': Quantity(500, g)
                    }
                ]
            },
        ]
    })


def complex_database() -> Database:
    return parse({
        ('database', '1.0'): [
            {
                'name': 'A',
                'exchanges': [
                    {
                        'name': 'A',
                        'type': 'production',
                        'quantity': Quantity(1, kWh),
                        'allocation': 1
                    },
                    {
                        'name': 'S1',
                        'type': 'emission',
                        'quantity': Quantity(200, g),
                    }
                ]
            },
            {
                'name': 'B',
                'exchanges': [
                    {
                        'name': 'B',
                        'type': 'production',
                        'quantity': Quantity(1, kg),
                        'allocation': 0.75
                    },
                    {
                        'name': 'B2',
                        'type': 'production',
                        'quantity': Quantity(1, kg),
                        'allocation': 0.25
                    },
                    {
                        'name': 'A',
                        'type': 'technosphere',
                        'quantity': Quantity(4.0, kWh)
                    },
                    {
                        'name': 'S1',
                        'type': 'emission',
                        'quantity': Quantity(100, g),
                    }
                ]
            },
            {
                'name': 'C',
                'exchanges': [
                    {
                        'name': 'C',
                        'type': 'production',
                        'quantity': Quantity(4, metric_ton),
                        'allocation': 1
                    },
                    {
                        'name': 'A',
                        'type': 'technosphere',
                        'quantity': Quantity(1.0, kWh)
                    },
                    {
                        'name': 'B',
                        'type': 'technosphere',
                        'quantity': Quantity(200.0, kg)
                    }
                ]
            },
            {
                'name': 'D',
                'exchanges': [
                    {
                        'name': 'D',
                        'type': 'production',
                        'quantity': Quantity(1, MWh),
                        'allocation': 1
                    },
                    {
                        'name': 'A',
                        'type': 'technosphere',
                        'quantity': Quantity(1.0, kWh)
                    },
                    {
                        'name': 'B',
                        'type': 'technosphere',
                        'quantity': Quantity(2.0, metric_ton)
                    },
                    {
                        'name': 'D',
                        'type': 'technosphere',
                        'quantity': Quantity(0.5, MWh)
                    },
                    {
                        'name': 'S2',
                        'type': 'emission',
                        'quantity': Quantity(1, kg),
                    }
                ]
            },
            {
                'name': 'E',
                'exchanges': [
                    {
                        'name': 'E',
                        'type': 'production',
                        'quantity': Quantity(1, kg),
                        'allocation': 1
                    },
                    {
                        'name': 'A',
                        'type': 'technosphere',
                        'quantity': Quantity(1.0, MWh)
                    },
                    {
                        'name': 'S3',
                        'type': 'emission',
                        'quantity': Quantity(1, litre),
                    }
                ]
            },
        ]
    })


def complex_realistic_database() -> Database:
    return parse(database_as_dict())
