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
import os

from gi.repository import GLib

from eosclubhouse import config


class QuestStringCatalog:

    _string_dict = {}

    def __init__(self):
        if self._string_dict:
            return
        self._load_csv()

    @classmethod
    def _load_csv(class_):
        strings = {}

        file_name = os.path.basename(config.QUESTS_STRINGS_CSV)
        dirs = [config.QUESTS_STRINGS_CSV,
                os.path.join(GLib.get_user_data_dir(), 'quests', file_name)]

        for csv_path in dirs:
            if not os.path.exists(csv_path):
                continue

            with open(csv_path, 'r') as csv_file:
                for key, value, _character in csv.reader(csv_file):
                    strings[key] = value

        class_._string_dict = strings

    @classmethod
    def get_string(class_, key):
        return class_._string_dict.get(key)


# Convenience "QuestString" method to get a string from the catalog
QS = QuestStringCatalog().get_string
