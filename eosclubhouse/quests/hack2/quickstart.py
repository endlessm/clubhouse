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


class Quickstart(Quest):

    __tags__ = ['pathway:games']
    __auto_offer_info__ = {'confirm_before': False, 'start_after': 0}
    __dismissible_messages__ = False

    def setup(self):
        self.auto_offer = True
        # Hide quest in UI
        self.skippable = True
        self._clubhouse_state = ClubhouseState()

    def step_begin(self):
        # Disable the characters in the UI to prevent launching any
        # other quest while the player is running the quickstart:
        self._clubhouse_state.characters_disabled = True
        self.wait_confirm('WELCOME1')
        action = self.show_choices_message('WELCOME2', ('POSITIVE', None, True),
                                           ('NEGATIVE', None, False)).wait()
        if action.future.result():
            self.highlight_nav('CLUBHOUSE')
            self.wait_confirm('HACKSWITCH1')
            self.highlight_nav('')
            # If the user played with the hack switch before the
            # explanation, we reset to normal:
            if not self._clubhouse_state.lights_on:
                self._clubhouse_state.lights_on = True
            self._clubhouse_state.hack_switch_highlighted = True
            skip_action = self.show_confirm_message('HACKSWITCH2',
                                                    confirm_label="I'd prefer not to, but thanks.")
            user_action = self.connect_clubhouse_changes(['lights-on'])
            self.wait_for_one([skip_action, user_action])
            self._clubhouse_state.hack_switch_highlighted = False
            if skip_action.is_done():
                # Automatically turn the lights off because the player
                # wants to skip using the switcher:
                self._clubhouse_state.lights_on = False
            skip_action = self.show_confirm_message('HACKSWITCH3', confirm_label='OK, I see.')
            user_action = self.connect_clubhouse_changes(['lights-on'])
            self.wait_for_one([skip_action, user_action])
            if skip_action.is_done():
                # Automatically turn the lights on because the player
                # wants to skip using the switcher:
                self._clubhouse_state.lights_on = True
            self.wait_confirm('ACTIVITIES')
        else:
            self.wait_confirm('DECLINE')

        self.show_message('END1', choices=[('Will do!', self.step_complete_and_stop)])

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
