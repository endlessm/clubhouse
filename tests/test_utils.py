import datetime
import unittest

from eosclubhouse.utils import convert_variant_arg


class TestVariantConversion(unittest.TestCase):

    def test_can_convert_variant(self):
        """Tests that we can convert Python dicts to GLib.Variant."""

        variant = convert_variant_arg({'hints_given': True})
        self.assertTrue(variant.unpack() == {'hints_given': True})

        with self.assertRaises(TypeError):
            convert_variant_arg({'no_serializable': datetime.datetime.now()})
