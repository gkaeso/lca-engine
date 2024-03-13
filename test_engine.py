from unittest import TestCase

import numpy as np

import model_fixture
from engine import LcaSystem


def expected_activity_domain(database):
    return {
        (*database.key, 'electricity'): 0,
        (*database.key, 'fertiliser'): 1,
        (*database.key, 'land transformation'): 2,
        (*database.key, 'phosphate, at mine'): 3,
        (*database.key, 'wheat grain'): 4,
        (*database.key, 'wheat straw'): 5
    }


class TestLcaSystem(TestCase):

    def test_technosphere_matrix__should_have_correct_domains(self):
        database = model_fixture.database()
        matrix = LcaSystem(database).technosphere_matrix

        self.assertEqual(matrix.input_domain, matrix.output_domain)
        self.assertEqual(matrix.input_domain._indices, expected_activity_domain(database))

    def test_technosphere_matrix__should_have_correct_array(self):
        database = model_fixture.database()
        matrix = LcaSystem(database).technosphere_matrix

        self.assertFalse((matrix.array - np.array([
            [3.6e9, 0, 0, 0, 0, 0],
            [-0.2 * 3.6e6, 1, 0, -2, 0, 0],
            [0, 0, 1e4, 0, 0, 0],
            [-0.1 * 3.6e6, 0, 0, 1, 0, 0],
            [0, -10, -500 * 1e4, 0, 1150, 0],  # cycle
            [0, -10, -500 * 1e4, 0, -50, 300],
        ])).any())

    def test_biosphere_matrix__should_have_correct_domains(self):
        database = model_fixture.database()
        matrix = LcaSystem(database).biosphere_matrix

        self.assertEqual(matrix.input_domain._indices, expected_activity_domain(database))
        self.assertEqual(matrix.output_domain._indices, {
            (database.name, database.version, 'carbon dioxide'): 0,
            (database.name, database.version, 'dinitrogen monoxide'): 1,
            (database.name, database.version, 'water'): 2,
        })

    def test_biosphere_matrix__should_have_correct_array(self):
        database = model_fixture.database()
        matrix = LcaSystem(database).biosphere_matrix

        self.assertEqual(matrix.array.shape, (6, 3))
        self.assertFalse((matrix.array - np.array([
            [5, 0, 0],
            [0, 0, 0],
            [6, 0, 0],
            [2, 0, 0],
            [100, 5, 1500],
            [100, 5, 1500],
        ])).any())
