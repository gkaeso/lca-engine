from functools import reduce
from typing import Self, override

import numpy as np

from engine_model import Domain, Matrix, System


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
        self._add_operator(_SupplyOperator(self._system.technosphere_matrix))
        return self

    def inventory(self) -> Self:
        self._add_operator(_InventoryOperator(self._system))
        return self

    def solve(self) -> Matrix:
        rhs = self._combine_operators()
        return Matrix(rhs.input_domain, rhs.output_domain,
                      np.linalg.solve(self._system.technosphere_matrix.array, rhs.array))

    def _combine_operators(self) -> Matrix:
        return reduce(lambda m1, m2: m1 * m2,
                      [operator.operate() for operator in self._operators[1:]],
                      self._operators[0].operate())

    def _add_operator(self, operator: _Operator):
        _OperatorValidator.validate(self._operators[-1], operator)
        self._operators.append(operator)

    def __len__(self) -> int:
        return len(self._operators)
