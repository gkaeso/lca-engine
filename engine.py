from collections import namedtuple
from dataclasses import dataclass
from functools import reduce
from sys import executable
from typing import Self, override

import numpy as np

from model import Database, Product, Substance

type Characterizable = Product | Substance
type ProductKey = namedtuple('ProductKey', ['database', 'version', 'name'])
type Key = ProductKey


class Domain:
    _indices: dict[ProductKey, int]
    _elements: dict[ProductKey, Characterizable]

    def __init__(self, indices: dict[ProductKey, int], elements: dict[ProductKey, Characterizable]):
        self._indices = indices
        self._elements = elements

    @property
    def indexed_elements(self) -> list[tuple[int, Characterizable]]:
        return [(self._indices[key], self._elements[key]) for key in self._indices.keys()]

    def index(self, key: ProductKey) -> int:
        return self._indices[key]

    def __len__(self) -> int:
        return len(self._indices)


def _domain_from(database: Database, func: executable) -> Domain:
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
    array: np.array

    def __mul__(self, other: Self) -> Self:
        return Matrix(self.input_domain, other.output_domain, np.dot(self.array, other.array))


def _arrays(database: Database, product_domain: Domain, substance_domain: Domain) -> tuple[np.ndarray, np.ndarray]:
    product_size = len(product_domain)
    biosphere_array = np.zeros((product_size, len(substance_domain)), dtype=np.float64)
    technosphere_array = np.zeros((product_size, product_size), dtype=np.float64)

    for product, biosphere_exchanges, technosphere_exchanges in [(product, activity.biosphere, activity.technosphere)
                                                                 for activity in database.activities
                                                                 for product in activity.production]:

        row = product_domain.index((database.name, database.version, product.name))

        for exchange in biosphere_exchanges:
            col = substance_domain.index((database.name, database.version, exchange.name))
            biosphere_array[row][col] += float(exchange.quantity.simplified) * product.allocation

        technosphere_array[row][row] += float(product.quantity.simplified)
        for exchange in technosphere_exchanges:
            col = product_domain.index((database.name, database.version, exchange.name))
            technosphere_array[row][col] -= float(exchange.quantity.simplified) * product.allocation

    return biosphere_array, technosphere_array


class System:
    biosphere_matrix: Matrix
    technosphere_matrix: Matrix

    def __init__(self, database: Database):
        product_domain = _domain_from(database, lambda db: db.sorted_products())
        substance_domain = _domain_from(database, lambda db: db.sorted_substances())

        biosphere_array, technosphere_array = _arrays(database, product_domain, substance_domain)
        self.biosphere_matrix = Matrix(product_domain, substance_domain, biosphere_array)
        self.technosphere_matrix = Matrix(product_domain, product_domain, technosphere_array)


class _Operator:
    input_domain: Domain
    output_domain: Domain

    def __init__(self, input_domain: Domain, output_domain: Domain):
        self.input_domain = input_domain
        self.output_domain = output_domain

    def operate(self) -> Matrix:
        raise NotImplementedError()


class _IdentityOperator(_Operator):

    def __init__(self, domain: Domain):
        super().__init__(domain, domain)

    @override
    def operate(self) -> Matrix:
        return Matrix(self.input_domain, self.output_domain, np.identity(len(self.input_domain), dtype=np.float64))


class _SupplyOperator(_Operator):
    _technosphere_matrix: Matrix

    def __init__(self, technosphere_matrix: Matrix):
        super().__init__(technosphere_matrix.input_domain, technosphere_matrix.output_domain)
        self._technosphere_matrix = technosphere_matrix

    def _reference_amount_array(self) -> np.ndarray:
        input_domain = self.input_domain
        size = len(input_domain)

        array = np.zeros((size, size), dtype=np.float64)
        for index, element in input_domain.indexed_elements:
            array[index][index] = float(element.quantity.simplified)

        return array

    @override
    def operate(self) -> Matrix:
        array = np.add(self._reference_amount_array(), np.negative(self._technosphere_matrix.array))
        return Matrix(self.input_domain, self.output_domain, array)


class _InventoryOperator(_Operator):
    _biosphere_matrix: Matrix

    def __init__(self, system: System):
        super().__init__(system.technosphere_matrix.input_domain, system.biosphere_matrix.output_domain)
        self._biosphere_matrix = system.biosphere_matrix

    @override
    def operate(self) -> Matrix:
        return self._biosphere_matrix


class _OperatorValidator:
    @staticmethod
    def validate(previous_operator: _Operator, new_operator: _Operator):
        if new_operator.input_domain is not previous_operator.output_domain:
            raise ValueError(f"{new_operator.__class__} operator incompatible with {previous_operator} output domain")


class OperatorChain:
    _system: System
    _input_domain: Domain
    _output_domain: Domain
    _operators: list[_Operator]

    def __init__(self, system: System):
        self._system = system
        self._input_domain = self._system.technosphere_matrix.input_domain
        self._output_domain = self._system.technosphere_matrix.output_domain
        self._operators = [_IdentityOperator(self._input_domain)]

    def supply(self) -> Self:
        operator = _SupplyOperator(self._system.technosphere_matrix)
        _OperatorValidator.validate(self._operators[-1], operator)
        self._operators.append(operator)
        return self

    def inventory(self) -> Self:
        operator = _InventoryOperator(self._system)
        _OperatorValidator.validate(self._operators[-1], operator)
        self._operators.append(operator)
        return self

    def solve(self) -> Matrix:
        rhs = self._combine_operators()
        return Matrix(rhs.input_domain, rhs.output_domain,
                      np.linalg.solve(self._system.technosphere_matrix.array, rhs.array))

    def __len__(self) -> int:
        return len(self._operators)

    def _combine_operators(self) -> Matrix:
        return reduce(lambda m1, m2: m1 * m2,
                      [operator.operate() for operator in self._operators[1:]],
                      self._operators[0].operate())
