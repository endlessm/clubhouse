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

import configparser
import csv
import gi
import glob
import itertools
import json
gi.require_version('Json', '1.0')
import os
import time
import datetime

from collections import OrderedDict
from enum import Enum
from gi.repository import GLib, GObject, Json
from string import Template

from eosclubhouse import config, logger


def get_alternative_quests_dir():
    return os.path.join(GLib.get_home_dir(), 'quests')


class _CircleList(list):
    def __getitem__(self, key):
        key = key % len(self)
        return super().__getitem__(key)


class DictFromCSV:

    _csv_dict = {}

    def __init__(self, csv_path, ignore_header=False):
        if self._csv_dict:
            return
        self.load_csv(csv_path, ignore_header)

    @classmethod
    def _do_load_csv(class_, csv_path, contents, ignore_header):
        with open(csv_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            if ignore_header:
                next(reader, [])
            for row in reader:
                class_.set_key_value_from_csv_row(row, contents)

    @classmethod
    def load_csv(class_, csv_original_path, ignore_header):
        contents = {}

        file_name = os.path.basename(csv_original_path)
        dirs = [csv_original_path, os.path.join(get_alternative_quests_dir(), file_name)]

        for csv_or_dir_path in dirs:
            if not os.path.exists(csv_or_dir_path):
                continue

            if not os.path.isdir(csv_or_dir_path):
                class_._do_load_csv(csv_or_dir_path, contents, ignore_header)
                continue

            for csv_path in glob.glob(os.path.join(csv_or_dir_path, '*csv')):
                class_._do_load_csv(csv_path, contents, ignore_header)

        class_._csv_dict = contents

    @classmethod
    def get_dict(class_):
        return class_._csv_dict

    @classmethod
    def set_key_value_from_csv_row(class_, csv_row, contents_dict):
        raise NotImplementedError()


class _ListFromCSV:

    _csv_list = []

    def __init__(self, csv_path):
        if self._csv_list:
            return
        self._load_csv(csv_path)

    @classmethod
    def get_list(class_):
        return class_._csv_list

    @classmethod
    def _load_csv(class_, csv_path):
        first = True
        with open(csv_path, 'r') as csv_file:
            for row in csv.reader(csv_file):
                if not first:
                    class_.append_value_from_csv_row(row, class_._csv_list)
                else:
                    first = False

    @classmethod
    def append_value_from_csv_row(class_, csv_row, contents):
        raise NotImplementedError()


class QuestStringCatalog(DictFromCSV):

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
    def get_loop_messages(class_, key, start=1):
        messages = _CircleList()
        for index in itertools.count(start=start):
            message_id = f'{key}_{index}'
            if class_.get_info(message_id) is None:
                break
            messages.append(message_id)

        return messages

    @classmethod
    def set_key_value_from_csv_row(class_, csv_row, contents_dict):
        if len(csv_row) == 6:
            # TODO: Remove this when all the CSV files have 6 columns.
            key, txt, character_id, mood, sfx_sound, bg_sound = csv_row
        else:
            key, txt, character_id, mood, sfx_sound, bg_sound = (*csv_row, '')
        contents_dict[key] = {
            'txt': txt.strip(),
            'character_id': character_id.lower().strip(),
            'mood': mood.lower().strip(),
            'sfx_sound': sfx_sound.lower().strip(),
            'bg_sound': bg_sound.lower().strip()
        }


class QuestItemDB(DictFromCSV):

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


class Episode(GObject.Object):

    def __init__(self, id_, number=1, season=None, name=None, description='',
                 badge_x=None, badge_y=None):
        super().__init__()

        self.id = id_
        self.number = number
        self.season = season
        self.name = name if name is not None else id_
        self.description = description
        self.badge_x = badge_x if badge_x is not None else 240
        self.badge_y = badge_y if badge_y is not None else 540
        self.is_available = False
        self.is_current = False

    def is_complete(self):
        return self.percentage_complete == 100

    percentage_complete = GObject.Property(type=int, default=0)


class EpisodesDB(DictFromCSV):

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
                episode_id, season, name, badge_x, badge_y, description = row
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

                contents[episode_id] = Episode(episode_id, number, season, name, description,
                                               badge_x, badge_y)

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

    @classmethod
    def get_episodes_in_season(class_, season):
        return [episode for key, episode in class_.get_all_episodes() if episode.season == season]


class NewsFeedItem():
    def __init__(self, date, character, image, image_href, text):
        super().__init__()
        self.date = datetime.date.fromisoformat(date.strip())
        self.character = character.lower().strip()
        self.image = image.lower().strip()
        self.image_href = image_href.strip()
        self.text = text.strip()


class NewsFeedDB(_ListFromCSV):
    def __init__(self):
        super().__init__(config.NEWSFEED_CSV)

    @classmethod
    def append_value_from_csv_row(class_, csv_row, contents):
        contents.append(NewsFeedItem(*csv_row))


class _ClubhouseStateImpl(GObject.GObject):

    current_page = GObject.Property(type=GObject.TYPE_PYOBJECT)
    lights_on = GObject.Property(type=bool, default=True)
    hack_switch_highlighted = GObject.Property(type=bool, default=False)
    user_button_highlighted = GObject.Property(type=bool, default=False)
    window_is_visible = GObject.Property(type=bool, default=False)
    characters_disabled = GObject.Property(type=bool, default=False)
    has_extension = GObject.Property(type=bool, default=False)
    nav_attract_state = GObject.Property(type=GObject.TYPE_PYOBJECT)


class ClubhouseState:
    '''Singleton that represents a Clubhouse state.'''

    Page = Enum('Page', ['CLUBHOUSE', 'PATHWAYS', 'NEWS', 'CHARACTER'])

    _impl = None

    def __init__(self):
        if ClubhouseState._impl is None:
            ClubhouseState._impl = _ClubhouseStateImpl()
            ClubhouseState._impl.current_page = ClubhouseState.Page.CLUBHOUSE
            ClubhouseState._impl.nav_attract_state = None

    def __getattr__(self, name):
        return getattr(self._impl, name)

    def __setattr__(self, name, value):
        setattr(self._impl, name, value)

    def __hasattr__(self, name):
        return hasattr(self._impl, name)


class MessageTemplate(Template):
    """Template for Clubhouse messages."""

    delimiter = '{{'
    pattern = r'''
    \{{(?:
       (?P<escaped>\#) |            # Expression {{# }} will escape the template: {{ }}
       (?P<named>[^\[{}\#]+)}} |    # These characters can't be used in names: #, {, and }
       \b\B(?P<braced>) |           # Braced names disabled
       (?P<invalid>)
    )
    '''


def get_flatpak_sandbox():
    info_filename = '/.flatpak-info'
    if not os.path.exists(info_filename):
        # If /.flatpak-info file doesn't exists is the host system
        return ''

    config = configparser.ConfigParser()
    config.read(info_filename)
    instance = config['Instance']
    sandbox = instance['app-path']
    commit = instance.get('app-commit', None)

    # replace the current commit id with 'active'
    if commit:
        sandbox = sandbox.replace(commit, 'active')

    return sandbox


def convert_variant_arg(variant):
    """Convert Python object to GLib.Variant"""
    if isinstance(variant, GLib.Variant):
        return variant

    if isinstance(variant, bool):
        return GLib.Variant('b', variant)

    if isinstance(variant, str):
        return GLib.Variant('s', variant)

    if isinstance(variant, dict):
        try:
            json_str = json.dumps(variant)
            return Json.gvariant_deserialize_data(json_str, -1, None)
        except Exception:
            raise TypeError('Error: the given Python dict can\'t be '
                            'converted to json or GLib.Variant')

    raise TypeError('Error: value is not a Python dict or GLib.Variant')


def triangle_area(a, b, c):
    return abs(a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1]))


def inside_triangle(p, a, b, c):
    abc_area = triangle_area(a, b, c)
    pbc_area = triangle_area(p, b, c)
    pac_area = triangle_area(p, a, c)
    pab_area = triangle_area(p, a, b)

    return abc_area - (pbc_area + pac_area + pab_area) == 0


class Version(list):
    def __init__(self, version_string, ignore_micro=False):
        n = 2 if ignore_micro else 3
        list.__init__(self, [int(s) for s in version_string.split('.')[:n]])
