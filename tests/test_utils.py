import datetime
import unittest

from eosclubhouse.utils import convert_variant_arg, Version


class TestVariantConversion(unittest.TestCase):

    def test_can_convert_variant(self):
        """Tests that we can convert Python dicts to GLib.Variant."""

        variant = convert_variant_arg({'hints_given': True})
        self.assertTrue(variant.unpack() == {'hints_given': True})

        with self.assertRaises(TypeError):
            convert_variant_arg({'no_serializable': datetime.datetime.now()})


class TestVersion(unittest.TestCase):
    # Test parsing
    def test_parsing(self):
        """Tests Version constructor parsing"""
        v = Version('1.2.3')
        self.assertTrue(v[0] == 1)
        self.assertTrue(v[1] == 2)
        self.assertTrue(v[2] == 3)

        v = Version('3.4')
        self.assertTrue(v[0] == 3)
        self.assertTrue(v[1] == 4)
        self.assertTrue(len(v) == 2)

        v = Version('3.4.5', ignore_micro=True)
        self.assertTrue(v[0] == 3)
        self.assertTrue(v[1] == 4)
        self.assertTrue(len(v) == 2)

    # <
    def test_lt(self):
        """Tests Version __lt__ operator"""
        self.assertTrue(Version('1.2.3') < Version('1.2.4'))
        self.assertTrue(Version('1.2.3') < Version('1.3.3'))
        self.assertTrue(Version('1.2.3') < Version('2.2.3'))
        self.assertFalse(Version('1.2.4') < Version('1.2.3'))
        self.assertFalse(Version('1.3.3') < Version('1.2.3'))
        self.assertFalse(Version('2.2.3') < Version('1.2.3'))

    # >
    def test_gt(self):
        """Tests Version __gt__ operator"""
        self.assertFalse(Version('1.2.3') > Version('1.2.4'))
        self.assertFalse(Version('1.2.3') > Version('1.3.3'))
        self.assertFalse(Version('1.2.3') > Version('2.2.3'))
        self.assertTrue(Version('1.2.4') > Version('1.2.3'))
        self.assertTrue(Version('1.3.3') > Version('1.2.3'))
        self.assertTrue(Version('2.2.3') > Version('1.2.3'))

    # <=
    def test_le(self):
        """Tests Version __le__ operator"""
        self.assertTrue(Version('1.2.3') <= Version('1.2.3'))
        self.assertTrue(Version('1.2.3') <= Version('1.2.4'))
        self.assertTrue(Version('1.2.3') <= Version('1.3.3'))
        self.assertTrue(Version('1.2.3') <= Version('2.2.3'))
        self.assertFalse(Version('1.2.4') <= Version('1.2.3'))
        self.assertFalse(Version('1.3.3') <= Version('1.2.3'))
        self.assertFalse(Version('2.2.3') <= Version('1.2.3'))

    # >=
    def test_ge(self):
        """Tests Version __ge__ operator"""
        self.assertTrue(Version('1.2.3') >= Version('1.2.3'))
        self.assertFalse(Version('1.2.3') >= Version('1.2.4'))
        self.assertFalse(Version('1.2.3') >= Version('1.3.3'))
        self.assertFalse(Version('1.2.3') >= Version('2.2.3'))
        self.assertTrue(Version('1.2.4') >= Version('1.2.3'))
        self.assertTrue(Version('1.3.3') >= Version('1.2.3'))
        self.assertTrue(Version('2.2.3') >= Version('1.2.3'))

    # ==
    def test_eq(self):
        """Tests Version __eq__ operator"""
        self.assertTrue(Version('1.2.3') == Version('1.2.3'))
        self.assertFalse(Version('1.2.0') == Version('1.2.1'))
        self.assertFalse(Version('1.2.0') == Version('1.1.0'))
        self.assertFalse(Version('1.2.0') == Version('2.2.0'))

    # !=
    def test_ne(self):
        """Tests Version __ne__ operator"""
        self.assertFalse(Version('1.2.3') != Version('1.2.3'))
        self.assertTrue(Version('1.2.0') != Version('1.2.1'))
        self.assertTrue(Version('1.2.0') != Version('1.1.0'))
        self.assertTrue(Version('1.2.0') != Version('2.2.0'))

