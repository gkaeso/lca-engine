from collections import namedtuple
from dataclasses import dataclass
from sys import executable

import numpy as np

from model import Database, Product, Substance

type Characterizable = Product | Substance
type ProductKey = namedtuple('ProductKey', ['database', 'version', 'name'])
type Key = ProductKey


@dataclass
class Domain:
    indices: dict[ProductKey, int]
    elements: dict[ProductKey, Characterizable]

    def index(self, key: ProductKey) -> int:
        return self.indices[key]

    def __len__(self) -> int:
        return len(self.indices)


def domain_from(database: Database, func: executable) -> Domain:
    indices, elements = {}, {}
    objects = func(database)
    for obj, index in zip(objects, range(len(objects))):
        key: Key = (database.name, database.version, obj.name)
        indices[key] = index
        elements[key] = obj
    return Domain(indices, elements)


@dataclass
class Matrix:
    input_domain: Domain
    output_domain: Domain
    values: np.array


def _arrays(database: Database, product_domain: Domain, substance_domain: Domain) -> tuple[np.ndarray, np.ndarray]:
    product_size = len(product_domain)
    biosphere_array = np.zeros((product_size, len(substance_domain)))
    technosphere_array = np.zeros((product_size, product_size))

    for product, biosphere_exchanges, technosphere_exchanges in [(product, activity.biosphere, activity.technosphere)
                                                                 for activity in database.activities
                                                                 for product in activity.production]:

        row = product_domain.index((database.name, database.version, product.name))

        for exchange in biosphere_exchanges:
            col = substance_domain.index((database.name, database.version, exchange.name))
            biosphere_array[row][col] = float(exchange.quantity.simplified)

        technosphere_array[row][row] += float(product.quantity.simplified)
        for exchange in technosphere_exchanges:
            col = product_domain.index((database.name, database.version, exchange.name))
            technosphere_array[row][col] -= float(exchange.quantity.simplified)

    return biosphere_array, technosphere_array


class LcaSystem:
    biosphere_matrix: Matrix
    technosphere_matrix: Matrix

    def __init__(self, database: Database):
        product_domain = domain_from(database, lambda db: db.sorted_products())
        substance_domain = domain_from(database, lambda db: db.sorted_substances())

        biosphere_array, technosphere_array = _arrays(database, product_domain, substance_domain)
        self.biosphere_matrix = Matrix(product_domain, substance_domain, biosphere_array)
        self.technosphere_matrix = Matrix(product_domain, product_domain, technosphere_array)
