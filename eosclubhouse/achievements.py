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
from collections import namedtuple
from enum import IntEnum

from eosclubhouse import config, logger
from eosclubhouse.utils import DictFromCSV

from gi.repository import EosMetrics, GLib, GObject


ACHIEVEMENT_POINTS_EVENT = '86521913-bfa3-4d13-b511-a03d4e339d2f'
ACHIEVEMENT_EVENT = '62ce2e93-bfdc-4cae-af4c-54068abfaf02'


Achievement = namedtuple('Achievement', ['id', 'name', 'description',
                                         'points_needed_per_skillset'])


class _AchievementsManager(GObject.Object):

    __gsignals__ = {
        'achievement-achieved': (
            GObject.SignalFlags.RUN_FIRST, None, (object, )
        ),
    }

    def __init__(self):
        self._achievements = {}
        self._empty_state_achievement = None
        self._points_per_skillset = {}
        super().__init__()

    def achieved(self, achievement, points_per_skillset=None):
        if points_per_skillset is None:
            points_per_skillset = self._points_per_skillset

        for skillset, points_needed in achievement.points_needed_per_skillset.items():
            if points_needed > points_per_skillset[skillset]:
                return False

        return True

    def load_achievement_row(self, row):
        id_ = row[AchievementsDB.Index.ID - 1].lower().strip()
        skillset = row[AchievementsDB.Index.SKILLSET - 1].upper().strip()
        points_needed = int(row[AchievementsDB.Index.POINTS_NEEDED - 1])

        if id_ in self._achievements:
            # Update existing achievement from the row.
            self._achievements[id_].points_needed_per_skillset[skillset] = points_needed

        else:
            # Or create a new achievement from the row.
            achievement = Achievement(
                id=id_,
                name=row[AchievementsDB.Index.NAME - 1].strip(),
                description=row[AchievementsDB.Index.DESCRIPTION - 1].strip(),
                points_needed_per_skillset={
                    skillset: points_needed,
                },
            )

            if id_ == AchievementsDB.EMPTY_STATE_ID:
                self._empty_state_achievement = achievement
                return

            self._achievements[id_] = achievement

        if skillset not in self._points_per_skillset:
            self._points_per_skillset[skillset] = 0

    @property
    def skillsets(self):
        return self._points_per_skillset.keys()

    def get_achievements_achieved(self):
        return [a for a in self._achievements.values() if self.achieved(a)]

    def add_points(self, skillset, points, record_points=False):
        skillset = skillset.upper()

        if skillset not in self._points_per_skillset:
            logger.warning('Not adding points to skillset %s, no achievements requiring it.',
                           skillset)
            return

        previous_points = self._points_per_skillset.copy()
        self._points_per_skillset[skillset] += points
        if record_points:
            self._record_points(skillset, points)

        logger.info('Skillset %s incremented by %r, now at %r', skillset, points,
                    self._points_per_skillset[skillset])

        for achievement in self._achievements.values():
            if skillset not in achievement.points_needed_per_skillset:
                # Filter the achievements that won't get achieved by
                # this skillset.
                continue

            if not self.achieved(achievement, previous_points) and self.achieved(achievement):
                self.emit('achievement-achieved', achievement)
                if record_points:
                    self._record_achievement(skillset, achievement)

    def _record_points(self, skillset, points):
        recorder = EosMetrics.EventRecorder.get_default()
        variant = GLib.Variant('(sii)', (skillset, points,
                                         self._points_per_skillset[skillset]))
        recorder.record_event(ACHIEVEMENT_POINTS_EVENT, variant)

    def _record_achievement(self, skillset, achievement):
        recorder = EosMetrics.EventRecorder.get_default()
        variant = GLib.Variant('(ss)', (achievement.id, achievement.name))
        recorder.record_event(ACHIEVEMENT_EVENT, variant)

    def _get_empty_state_achievement(self):
        return self._empty_state_achievement

    empty_state_achievement = property(_get_empty_state_achievement)


class AchievementsDB(DictFromCSV):

    Index = IntEnum('Index', ['ID', 'NAME', 'DESCRIPTION', 'SKILLSET', 'POINTS_NEEDED'])

    EMPTY_STATE_ID = 'empty-state'
    _manager = None

    def __init__(self):
        if self._manager:
            return

        self._setup_manager()
        super().__init__(config.ACHIEVEMENTS_CSV, ignore_header=True)

    @property
    def manager(self):
        return self._manager

    @classmethod
    def _setup_manager(class_):
        class_._manager = _AchievementsManager()

    @classmethod
    def set_key_value_from_csv_row(class_, csv_row, contents_dict):
        class_._manager.load_achievement_row(csv_row)
