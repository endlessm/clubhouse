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


def get_alternative_quests_dir():
    return os.path.join(GLib.get_user_data_dir(), 'quests')


class _DictFromCSV:

    _csv_dict = {}

    def __init__(self, csv_path):
        if self._csv_dict:
            return
        self.load_csv(csv_path)

    @classmethod
    def load_csv(class_, csv_original_path):
        contents = {}

        file_name = os.path.basename(csv_original_path)
        dirs = [csv_original_path, os.path.join(get_alternative_quests_dir(), file_name)]

        for csv_path in dirs:
            if not os.path.exists(csv_path):
                continue

            with open(csv_path, 'r') as csv_file:
                for row in csv.reader(csv_file):
                    class_.set_key_value_from_csv_row(row, contents)

        class_._csv_dict = contents

    @classmethod
    def get_dict(class_):
        return class_._csv_dict

    @classmethod
    def set_key_value_from_csv_row(class_, csv_row, contents_dict):
        raise NotImplementedError()


class QuestStringCatalog(_DictFromCSV):

    def __init__(self):
        super().__init__(config.QUESTS_STRINGS_CSV)

    @classmethod
    def get_string(class_, key):
        return class_.get_dict().get(key)

    @classmethod
    def set_key_value_from_csv_row(class_, csv_row, contents_dict):
        key, value = csv_row[0], csv_row[1]
        contents_dict[key] = value


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
        item_id, icon, name = csv_row
        contents_dict[item_id] = (icon, name)

    @classmethod
    def get_icon_path(self, icon_name):
        return os.path.join(config.ITEM_ICONS_DIR, icon_name)


# Convenience "QuestString" method to get a string from the catalog
QS = QuestStringCatalog().get_string
