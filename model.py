from dataclasses import dataclass
from enum import Enum
from typing import Self

from quantities import Quantity


@dataclass
class CharacterizationFactor:
    compartment: str
    sub_compartment: str
    quantity: Quantity


class ExchangeType(Enum):
    # technosphere output
    PRODUCTION = 'production'

    # technosphere input
    TECHNOSPHERE = 'technosphere'

    # biosphere output
    EMISSION = 'emission'

    # biosphere input
    BIOSPHERE = 'biosphere'


@dataclass
class Exchange:
    name: str
    quantity: Quantity
    # type: ExchangeType


@dataclass
class Substance:
    name: str

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        return isinstance(other, Substance) and hash(self) == hash(other)


@dataclass
class BiosphereExchange(Exchange):
    flow_type: str


@dataclass
class Product(Exchange):
    allocation: float

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        return isinstance(other, Product) and hash(self) == hash(other)


@dataclass
class TechnosphereExchange(Exchange):
    pass


@dataclass
class Activity:
    name: str
    production: list[Product]
    biosphere: list[Exchange]
    technosphere: list[Exchange]


@dataclass
class Database:
    name: str
    version: str
    activities: list[Activity]

    @property
    def key(self) -> tuple[str, str]:
        return self.name, self.version

    def sorted_products(self) -> list[Product]:
        return sorted([p for a in self.activities for p in a.production], key=lambda p: p.name)

    def sorted_substances(self) -> list[Substance]:
        substances: set[Substance] = set()
        for activity in self.activities:
            substances.update([Substance(b.name) for b in activity.biosphere])
        return sorted(substances, key=lambda s: s.name)

    @classmethod
    def from_dict(cls, d: dict) -> Self:
        (database_name, database_version), activity_dicts = list(d.items())[0]

        activities: list[Activity] = []
        for activity_dict in activity_dicts:
            products: list[Product] = []
            biosphere: list[BiosphereExchange] = []
            technosphere: list[TechnosphereExchange] = []
            for exchange in activity_dict['exchanges']:
                exchange_name, quantity = exchange['name'], exchange['quantity']
                if exchange['type'] == 'production':
                    products.append(Product(exchange_name, quantity, exchange['allocation']))
                elif exchange['type'] in ('biosphere', 'emission'):
                    biosphere.append(BiosphereExchange(exchange_name, quantity, exchange['type']))
                elif exchange['type'] == 'technosphere':
                    technosphere.append(TechnosphereExchange(exchange_name, quantity))
            activities.append(Activity(activity_dict['name'], products, biosphere, technosphere))

        return Database(database_name, database_version, activities)
