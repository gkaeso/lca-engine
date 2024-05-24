import numpy as np


def _almost_equal(array: np.ndarray, reference: np.ndarray, rel_error: float) -> bool:
    row_size, col_size = array.shape
    for i in range(row_size):
        for j in range(col_size):
            value = array[i][j]
            reference_value = reference[i][j]
            relative_diff = abs(abs(value - reference_value) / reference_value) if reference_value != 0 else rel_error
            if relative_diff > rel_error:
                return False
    return True


# using custom almost_equal function because the one from numpy has too restrictive checks
def almost_equal(array1: np.ndarray, array2: np.ndarray, rel_error: float = 1e-8) -> bool:
    return array1.shape == array2.shape and _almost_equal(array1, array2, rel_error)
