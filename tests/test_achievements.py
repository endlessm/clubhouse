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
import unittest

from eosclubhouse.achievements import _AchievementsManager


class TestAchievementsManager(unittest.TestCase):

    _rows = [
        ['cat-herder', 'Cat Herder', '', 'FELIX', '3'],
        ['beginner-reader', 'Beginner Reader', '', 'NARRATIVE', '5'],
        ['mixed-badge', 'Mixed', '', 'FELIX', '1'],
        ['mixed-badge', 'Mixed', '', 'NARRATIVE', '1'],
    ]

    def setUp(self):
        self.manager = _AchievementsManager()

    def _load_rows(self):
        for row in self._rows:
            self.manager.load_achievement_row(row)

    def _get_achieved_ids(self):
        return [a.id for a in self.manager.get_achievements_achieved()]

    def test_can_load(self):
        """Tests that can load achievements."""
        self.assertNotIn('FELIX', self.manager.skillsets)

        self._load_rows()

        achieved = self.manager.get_achievements_achieved()
        self.assertEqual(achieved, [])

        self.assertIn('FELIX', self.manager.skillsets)

    def test_can_become_achieved(self):
        """Tests that can check which achievements are achieved and become achieved."""
        self._load_rows()
        self.assertNotIn('mixed-badge', self._get_achieved_ids())
        self.manager.add_points('FELIX', 1)
        self.manager.add_points('NARRATIVE', 1)
        self.assertIn('mixed-badge', self._get_achieved_ids())
        self.assertNotIn('beginner-reader', self._get_achieved_ids())
        self.manager.add_points('NARRATIVE', 7)
        self.assertIn('beginner-reader', self._get_achieved_ids())
        self.assertNotIn('cat-herder', self._get_achieved_ids())
        self.manager.add_points('FELIX', 2)
        self.assertIn('cat-herder', self._get_achieved_ids())
