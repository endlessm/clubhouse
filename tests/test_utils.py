#
# Copyright © 2020 Endless OS Foundation LLC.
#
# This file is part of clubhouse
# (see https://github.com/endlessm/clubhouse).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
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
