from collections import namedtuple
from dataclasses import dataclass
from enum import Enum

from quantities import Quantity


@dataclass
class Substance:
    name: str

    @property
    def key(self) -> str:
        return self.name

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other) -> bool:
        return isinstance(other, Substance) and hash(self) == hash(other)


@dataclass
class CharacterizationFactor:
    substance: Substance
    compartment: str
    sub_compartment: str
    quantity: Quantity

    def __hash__(self) -> int:
        return hash(f'{self.substance.name}|{self.compartment}|{self.sub_compartment}')

    def __eq__(self, other) -> bool:
        return isinstance(other, CharacterizationFactor) and hash(self) == hash(other)


@dataclass
class Indicator:
    name: str
    unit: str
    factors: list[CharacterizationFactor]

    @property
    def key(self) -> str:
        return self.name


@dataclass
class Method:
    name: str
    indicators: list[Indicator]


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


type DatabaseKey = namedtuple('DatabaseKey', ['database', 'version'])
type ProductKey = namedtuple('ProductKey', ['database_key', 'name'])


@dataclass
class Product(Exchange):
    allocation: float
    database_key: DatabaseKey

    @property
    def key(self) -> ProductKey:
        return self.database_key, self.name

    def __hash__(self) -> int:
        return hash(self.key)

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
    def key(self) -> DatabaseKey:
        return self.name, self.version
