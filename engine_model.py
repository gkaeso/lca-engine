from dataclasses import dataclass
from typing import Self

import numpy as np

from lca_model import Database, Product, Substance, Method, Indicator, ProductKey

type Characterizable = Product | Substance | Indicator
type CharacterizableKey = ProductKey | str


class Domain:
    _indices: dict[CharacterizableKey, int]
    _elements: dict[CharacterizableKey, Characterizable]

    def __init__(self, indices: dict[CharacterizableKey, int], elements: dict[CharacterizableKey, Characterizable]):
        self._indices = indices
        self._elements = elements

    @property
    def indexed_elements(self) -> list[tuple[int, Characterizable]]:
        return [(self._indices[key], self._elements[key]) for key in self._indices.keys()]

    def index(self, key: CharacterizableKey) -> int:
        return self._indices[key]

    def __len__(self) -> int:
        return len(self._indices)


def _domain_from(characterizables: list[Characterizable]) -> Domain:
    indices, elements = {}, {}
    for index, obj in enumerate(characterizables):
        key: CharacterizableKey = obj.key
        indices[key] = index
        elements[key] = obj
    return Domain(indices, elements)


@dataclass
class Matrix:
    input_domain: Domain
    output_domain: Domain
    array: np.array

    def __mul__(self, other: Self) -> Self:
        if self.output_domain is not other.input_domain:
            raise ValueError(f'incompatible domains for matrix multiplication')
        return Matrix(self.input_domain, other.output_domain, np.dot(self.array, other.array))


def _arrays(database: Database, product_domain: Domain, substance_domain: Domain) -> tuple[np.ndarray, np.ndarray]:
    product_size = len(product_domain)
    biosphere_array = np.zeros((product_size, len(substance_domain)), dtype=np.float64)
    technosphere_array = np.zeros((product_size, product_size), dtype=np.float64)

    for product, biosphere_exchanges, technosphere_exchanges in [(product, activity.biosphere, activity.technosphere)
                                                                 for activity in database.activities
                                                                 for product in activity.production]:

        row = product_domain.index(product.key)

        for exchange in biosphere_exchanges:
            col = substance_domain.index((database.name, database.version, exchange.name))
            biosphere_array[row][col] += float(exchange.quantity.simplified) * product.allocation

        technosphere_array[row][row] += float(product.quantity.simplified)
        for exchange in technosphere_exchanges:
            col = product_domain.index((database.name, database.version, exchange.name))
            technosphere_array[row][col] -= float(exchange.quantity.simplified) * product.allocation

    return biosphere_array, technosphere_array


def _sorted_products(database: Database) -> list[Product]:
    return sorted([p for a in database.activities for p in a.production], key=lambda p: p.name)


def _sorted_substances(database: Database) -> list[Substance]:
    substances: set[Substance] = set()
    for activity in database.activities:
        substances.update([Substance(b.name) for b in activity.biosphere])
    return sorted(substances, key=lambda s: s.name)


def _sorted_indicators(method: Method) -> list[Indicator]:
    return sorted([i for i in method.indicators], key=lambda i: i.name)


class System:
    biosphere_matrix: Matrix
    technosphere_matrix: Matrix

    def __init__(self, database: Database):
        product_domain = _domain_from(_sorted_products(database))
        substance_domain = _domain_from(_sorted_substances(database))

        biosphere_array, technosphere_array = _arrays(database, product_domain, substance_domain)
        self.biosphere_matrix = Matrix(product_domain, substance_domain, biosphere_array)
        self.technosphere_matrix = Matrix(product_domain, product_domain, technosphere_array)


def _method_matrix(method: Method, substance_domain: Domain) -> Matrix:
    indicator_domain = _domain_from(_sorted_indicators(method))
    array = np.zeros((len(substance_domain), len(indicator_domain)), dtype=np.float64)
    for indicator in method.indicators:
        for factor in indicator.factors:
            row = substance_domain.index(factor.substance.key)
            col = indicator_domain.index(indicator.key)
            array[row][col] += factor.quantity.simplified
    return Matrix(substance_domain, indicator_domain, array)
