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
from eosclubhouse.libquest import Quest
from eosclubhouse.utils import ClubhouseState


class Lightswitch(Quest):

    __tags__ = ['pathway:games']

    def setup(self):
        # Hide quest in UI
        self.skippable = True
        self._clubhouse_state = ClubhouseState()

    def step_begin(self):
        self._item = 0
        return self.step_button_pressed, 'CHAT1'

    def step_button_pressed(self, msgid):
        skip_action = self.show_confirm_message(msgid)
        user_action = self.connect_clubhouse_changes(['lights-on'])
        self.wait_for_one([skip_action, user_action])
        if skip_action.is_done():
            # user clicked next button
            if msgid == 'CHAT5':
                self._clubhouse_state.lights_on = True
                self.wait_confirm('CHAT8')
                return self.step_complete_and_stop
            next_msgid = ['CHAT2', 'CHAT3', 'CHAT4', 'CHAT5'][self._item]
            self._item += 1
        if user_action.is_done():
            # user clicked light switch
            if msgid == 'CHAT5':
                self.wait_confirm('CHAT6')
            else:
                self.wait_confirm('CHAT7', timeout=4)
            return self.step_complete_and_stop
        return self.step_button_pressed, next_msgid

    def _back_to_normal(self):
        self._clubhouse_state.characters_disabled = False
        if not self._clubhouse_state.lights_on:
            self._clubhouse_state.lights_on = True

    def step_complete_and_stop(self):
        self._back_to_normal()
        super().step_complete_and_stop()

    def step_abort(self):
        self._back_to_normal()
        super().step_abort()
