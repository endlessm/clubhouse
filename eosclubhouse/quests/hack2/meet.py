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


class Meet(Quest):

    __tags__ = ['pathway:games', 'difficulty:easy']
    __pathway_order__ = 10

    def setup(self):
        self._clubhouse_state = ClubhouseState()

    def step_begin(self):
        self._clubhouse_state.characters_disabled = True
        self.wait_confirm('WELCOME1')
        self.wait_confirm('WELCOME2')
        self.highlight_nav('CLUBHOUSE')
        self.show_hints_message('GOBACK')
        self.connect_clubhouse_changes(['current-page']).wait()
        self.highlight_nav('')
        self.wait_confirm('EXPLAIN_MAIN1')
        self.wait_confirm('EXPLAIN_MAIN2')
        return self.step_pathways

    def step_pathways(self):
        # explain pathways
        self.highlight_nav('PATHWAYS')
        self.wait_confirm('EXPLAIN_PATHWAYS1')
        self.wait_confirm('EXPLAIN_PATHWAYS2')
        self.highlight_nav('')
        return self.step_profile

    def step_profile(self):
        # explain the profile
        self._clubhouse_state.user_button_highlighted = True
        for msgid in ['EXPLAIN_PROFILE1', 'EXPLAIN_PROFILE2', 'EXPLAIN_PROFILE3']:
            self.wait_confirm(msgid)
        self._clubhouse_state.user_button_highlighted = False
        # ask if player wants to change their name
        action = self.show_choices_message('CHANGE_NAME_ASK', ('CHANGE_NAME_YES', None, True),
                                           ('CHANGE_NAME_NO', None, False)).wait()
        if action.future.result():
            for msgid in ['CHANGE_NAME1', 'CHANGE_NAME2', 'CHANGE_NAME3', 'CHANGE_NAME4']:
                self.wait_confirm(msgid)
        return self.step_ending

    def step_ending(self):
        for msgid in ['END1', 'END2']:
            self.wait_confirm(msgid)
        self.wait_confirm('END3', confirm_label="See you!")
        self._clubhouse_state.characters_disabled = False
        return self.step_complete_and_stop

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
