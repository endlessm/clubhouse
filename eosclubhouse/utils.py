# Copyright (C) 2018 Endless Mobile, Inc.
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
# Authors:
#       Joaquim Rocha <jrocha@endlessm.com>
#       Noel Llopis <noel@endlessm.com>
#

import csv
import glob
import itertools
import os
import time

from collections import OrderedDict

from gi.repository import GLib

from eosclubhouse import config, logger


def get_alternative_quests_dir():
    return os.path.join(GLib.get_user_data_dir(), 'quests')


class _DictFromCSV:

    _csv_dict = {}

    def __init__(self, csv_path):
        if self._csv_dict:
            return
        self.load_csv(csv_path)

    @classmethod
    def _do_load_csv(class_, csv_path, contents):
        with open(csv_path, 'r') as csv_file:
            for row in csv.reader(csv_file):
                class_.set_key_value_from_csv_row(row, contents)

    @classmethod
    def load_csv(class_, csv_original_path):
        contents = {}

        file_name = os.path.basename(csv_original_path)
        dirs = [csv_original_path, os.path.join(get_alternative_quests_dir(), file_name)]

        for csv_or_dir_path in dirs:
            if not os.path.exists(csv_or_dir_path):
                continue

            if not os.path.isdir(csv_or_dir_path):
                class_._do_load_csv(csv_or_dir_path, contents)
                continue

            for csv_path in glob.glob(os.path.join(csv_or_dir_path, '*csv')):
                class_._do_load_csv(csv_path, contents)

        class_._csv_dict = contents

    @classmethod
    def get_dict(class_):
        return class_._csv_dict

    @classmethod
    def set_key_value_from_csv_row(class_, csv_row, contents_dict):
        raise NotImplementedError()


class QuestStringCatalog(_DictFromCSV):

    def __init__(self):
        super().__init__(config.QUESTS_STRINGS_DIR)

    @classmethod
    def get_info(class_, key):
        return class_.get_dict().get(key)

    @classmethod
    def get_string(class_, key):
        info = class_.get_info(key)
        if info is not None:
            return info['txt']

    @classmethod
    def get_hint_keys(class_, key):
        hint_keys = [key]
        for hint_index in itertools.count(start=1):
            hint_key = '{}_HINT{}'.format(key, hint_index)
            if class_.get_info(hint_key) is None:
                break
            hint_keys.append(hint_key)

        return hint_keys

    @classmethod
    def set_key_value_from_csv_row(class_, csv_row, contents_dict):
        key, txt, character_id, mood, open_dialog_sound = csv_row
        contents_dict[key] = {
            'txt': txt,
            'character_id': character_id.lower().strip(),
            'mood': mood.lower().strip(),
            'open_dialog_sound': open_dialog_sound.lower().strip(),
        }


class QuestItemDB(_DictFromCSV):

    def __init__(self):
        super().__init__(config.QUESTS_ITEMS_CSV)

    @classmethod
    def get_item(class_, key):
        return class_.get_dict().get(key)

    @classmethod
    def get_all_items(class_):
        return class_.get_dict().items()

    @classmethod
    def set_key_value_from_csv_row(class_, csv_row, contents_dict):
        item_id, *item_data = csv_row
        contents_dict[item_id] = item_data

    @classmethod
    def get_icon_path(self, icon_name):
        return os.path.join(config.ITEM_ICONS_DIR, icon_name)


# Convenience "QuestString" method to get a string from the catalog
QS = QuestStringCatalog().get_string


class Performance:

    _enabled = 'CLUBHOUSE_PERF_DEBUG' in os.environ

    @classmethod
    def timeit(class_, func):
        def _report_time_func(*args, **kwargs):
            start_time = time.time()

            result = func(*args, **kwargs)

            end_time = time.time()
            logger.info('%s : %3.3fms', str(func), (end_time - start_time) * 1000.0)

            return result

        return _report_time_func if class_._enabled else func


class Episode:
    def __init__(self, id_, number=1, season=None, name=None, badge_x=None, badge_y=None):
        self.id = id_
        self.number = number
        self.season = season
        self.name = name if name is not None else id_
        self.badge_x = badge_x if badge_x is None else 240
        self.badge_y = badge_y if badge_y is None else 540


class EpisodesDB(_DictFromCSV):

    def __init__(self):
        super().__init__(config.EPISODES_CSV)

    @classmethod
    def load_csv(class_, csv_path):
        contents = OrderedDict()

        class_._do_load_csv(csv_path, contents)
        class_._csv_dict = contents

    @classmethod
    def get_episode(class_, key):
        return class_.get_dict().get(key, Episode(key))

    @classmethod
    def get_all_episodes(class_):
        return class_.get_dict().items()

    @classmethod
    def _do_load_csv(class_, csv_path, contents):
        with open(csv_path, 'r') as csv_file:
            number = 0
            prev_season = None
            for row in csv.reader(csv_file):
                episode_id, season, name, badge_x, badge_y = row
                # using appearance order in the same session to number episodes
                if season != prev_season:
                    prev_season = season
                    number = 0
                number += 1

                try:
                    badge_x = int(badge_x)
                except ValueError:
                    badge_x = None

                try:
                    badge_y = int(badge_y)
                except ValueError:
                    badge_y = None

                contents[episode_id] = Episode(episode_id, number, season, name, badge_x, badge_y)

    @classmethod
    def get_previous_episodes(class_, current_episode):
        episode = class_.get_episode(current_episode)
        return [v for k, v in class_.get_all_episodes()
                if v.season == episode.season and v.number < episode.number]

    @classmethod
    def get_next_episodes(class_, current_episode):
        episode = class_.get_episode(current_episode)
        return [v for k, v in class_.get_all_episodes()
                if v.season == episode.season and v.number > episode.number]
