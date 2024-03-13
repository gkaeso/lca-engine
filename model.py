from dataclasses import dataclass
from enum import Enum

from quantities import Quantity


@dataclass
class CharacterizationFactor:
    compartment: str
    sub_compartment: str
    quantity: Quantity


@dataclass
class Substance:
    name: str

    # kfactors: list[CharacterizationFactor]

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        return isinstance(other, Substance) and hash(self) == hash(other)


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


@dataclass
class BiosphereExchange(Exchange):
    type: ExchangeType


@dataclass
class TechnosphereExchange(Exchange):
    pass


@dataclass
class Product(Exchange):
    allocation: float

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other) -> bool:
        return isinstance(other, Product) and hash(self) == hash(other)


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
