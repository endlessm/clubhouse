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
from eosclubhouse.utils import MessageTemplate
from clubhouseunittest import ClubhouseTestCase


class TestMessageTemplate(ClubhouseTestCase):

    def setUp(self):
        self._variables = {'user_name': 'Lisa', 'app_name': 'Fizzics'}

    def test_can_substitute(self):
        """Tests that templates can substitute names using the custom delimiter."""
        template = MessageTemplate('Hello {{user_name}}, nice to meet you')
        message = template.substitute(self._variables)
        self.assertEqual(message, 'Hello Lisa, nice to meet you')

    def test_doesnt_regress_code(self):
        """Tests that messages with code don't regress."""
        template = MessageTemplate('Please set `x = {"gravity": -9.8}` in {{app_name}}')
        message = template.substitute(self._variables)
        self.assertEqual(message, 'Please set `x = {"gravity": -9.8}` in Fizzics')

    def test_can_escape_substitution(self):
        """Tests that the format to substitute names can be escaped."""
        template = MessageTemplate('Hello {{#user_name}}, nice to meet you')
        message = template.substitute(self._variables)
        self.assertEqual(message, 'Hello {{user_name}}, nice to meet you')

    def test_fails_on_invalid_names(self):
        """Tests that names in templates can't have special characters."""
        for template_message in [
                'Hello {{user{name}}, nice to meet you',
                'Hello {{user}name}}, nice to meet you',
                'Hello {{user#name}}, nice to meet you',
        ]:
            template = MessageTemplate(template_message)
            with self.assertRaises(ValueError):
                template.substitute(self._variables)
