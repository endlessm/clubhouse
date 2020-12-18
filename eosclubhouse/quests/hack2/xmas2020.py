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
from eosclubhouse.libquest import Quest, Registry


class Xmas2020(Quest):
    __tags__ = ['pathway:operating system', 'since:1.4']
    __auto_offer_info__ = {
        'confirm_before': False,
        'start_after': 0,
    }
    __dismissible_messages__ = False

    def setup(self):
        self.auto_offer = True
        # Hide quest in UI
        self.skippable = True
        self.available_since = '2020-12-01'
        self.available_until = '2020-12-31'

    def step_begin(self):
        self.wait_confirm('HELLO1')
        action = self.show_choices_message('HELLO2', ('NOQUEST_POSITIVE', None, True),
                                           ('NOQUEST_NEGATIVE', None, False)).wait()
        if action.future.result():
            registry = Registry.get_or_create()
            registry.schedule_quest('Snow', **self.__auto_offer_info__)
            return self.step_complete_and_stop
        else:
            return self.step_abort

    def step_abort(self):
        self.complete = True
        super().step_abort()
