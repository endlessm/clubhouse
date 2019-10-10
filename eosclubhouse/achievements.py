from enum import IntEnum

from eosclubhouse import config, logger
from eosclubhouse.utils import DictFromCSV

from gi.repository import GObject


class Achievement:

    def __init__(self, data):
        self._data = data

    def achieved(self, points):
        return points >= self._data['points_needed']

    @property
    def id_(self):
        return self._data['id']

    @property
    def name(self):
        return self._data['name']

    @property
    def description(self):
        return self._data['description']

    @property
    def skillset(self):
        return self._data['skillset']

    @property
    def points_needed(self):
        return self._data['points_needed']

    @classmethod
    def new_from_csv_row(self, row):
        data = {
            'id': row[AchievementsDB.Index.ID - 1].lower().strip(),
            'name': row[AchievementsDB.Index.NAME - 1].strip(),
            'description': row[AchievementsDB.Index.DESCRIPTION - 1].strip(),
            'skillset': row[AchievementsDB.Index.SKILLSET - 1].upper().strip(),
            'points_needed': int(row[AchievementsDB.Index.POINTS_NEEDED - 1]),
        }
        return Achievement(data)


class _AchievementsManager(GObject.Object):

    _achievements = []
    _points_per_skillset = {}

    __gsignals__ = {
        'achievement-achieved': (
            GObject.SignalFlags.RUN_FIRST, None, (object, )
        ),
    }

    def __init__(self):
        super().__init__()

    def load_achievement(self, achievement):
        self._achievements.append(achievement)
        if achievement.skillset not in self._points_per_skillset:
            self._points_per_skillset[achievement.skillset] = 0

    @property
    def skillsets(self):
        return self._points_per_skillset.keys()

    def get_achievements_achieved(self):
        achievements_achieved = []
        for achievement in self._achievements:
            points = self._points_per_skillset[achievement.skillset]
            if achievement.achieved(points):
                achievements_achieved.append(achievement)
        return achievements_achieved

    def add_points(self, skillset, points):
        skillset = skillset.upper()

        if skillset not in self._points_per_skillset:
            logger.warning('Not adding points to skillset %s, no achievements requiring it.',
                           skillset)
            return

        previous_points = self._points_per_skillset[skillset]
        new_points = previous_points + points
        self._points_per_skillset[skillset] = new_points

        logger.debug('Skillset %s incremented by %r, now at %r', skillset, points, new_points)

        for achievement in self._achievements:
            if achievement.skillset != skillset:
                continue

            if not achievement.achieved(previous_points) and achievement.achieved(new_points):
                self.emit('achievement-achieved', achievement)


class AchievementsDB(DictFromCSV):

    Index = IntEnum('Index', ['ID', 'NAME', 'DESCRIPTION', 'SKILLSET', 'POINTS_NEEDED'])
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
        achievement = Achievement.new_from_csv_row(csv_row)
        class_._manager.load_achievement(achievement)
