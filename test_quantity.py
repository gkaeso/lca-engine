from unittest import TestCase

import quantities as qty
from quantities import Quantity, CompoundUnit, UnitQuantity


class QuantityTest(TestCase):

    def test_simple_unit(self):
        self.assertEqual(Quantity(1.0, qty.kilometer), Quantity(1e3, qty.meter))

    def test_same_dimension_different_units(self):
        self.assertEqual(Quantity(1.0, qty.kWh).rescale(qty.joule), Quantity(3.6e6, qty.joule))

    def test_international_system_of_units(self):
        self.assertEqual(Quantity(1.0, qty.kWh).simplified, Quantity(3.6e6, qty.joule))
        self.assertEqual(Quantity(1.0, qty.metric_ton).simplified, Quantity(1e3, qty.kg))

    def test_compound_unit(self):
        u = CompoundUnit('m**2*t')
        self.assertEqual(Quantity(1.0, u), Quantity(1e3, 'kg*m**2'))

    def test_custom_unit(self):
        u = UnitQuantity('microkelvin', qty.degK / 1e6, symbol='uK')
        self.assertEqual(Quantity(1e6, u), Quantity(1.0, qty.kelvin))
