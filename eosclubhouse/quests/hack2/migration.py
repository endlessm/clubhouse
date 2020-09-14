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
from eosclubhouse.system import Desktop
from eosclubhouse.utils import ClubhouseState


class Migration(Quest):

    __tags__ = ['pathway:games', 'skillset:Veteran']
    __dismissible_messages__ = False

    def setup(self):
        self.skippable = True
        self._clubhouse_state = ClubhouseState()

    def step_begin(self):
        for msgid in ['WELCOME', 'WELCOME2']:
            self.wait_confirm(msgid)
        return self.step_open_clubhouse

    def step_open_clubhouse(self):
        self.show_hints_message('OPENIT')
        Desktop.set_hack_icon_pulse(True)
        # @todo: we should use wait_for_app_in_foreground() here instead of
        # doing a busy wait, see https://phabricator.endlessm.com/T28521
        while not Desktop.is_app_in_foreground('com.hack_computer.Clubhouse'):
            self.pause(3)
        return self.step_explain_old_apps

    def step_explain_old_apps(self):
        self._clubhouse_state.characters_disabled = True
        # explain what we did to the old apps
        for msgid in ['OLDSTUFF1', 'OLDSTUFF2', 'OLDSTUFF3']:
            self.wait_confirm(msgid)
        self.complete = True
        for msgid in ['OLDSTUFF4', 'OLDSTUFF5']:
            self.wait_confirm(msgid)
        return self.step_explain_activities

    def step_explain_activities(self):
        self.wait_confirm('NEWSTUFF')
        # explain activities and how to play them
        for msgid in ['ACTIVITIES1', 'ACTIVITIES2', 'ACTIVITIES3']:
            self.wait_confirm(msgid)
        return self.step_explain_profile

    def step_explain_profile(self):
        # explain how the profile works and how to change your name
        self._clubhouse_state.user_button_highlighted = True
        self.wait_confirm('PROFILE1')
        self._clubhouse_state.user_button_highlighted = False
        for msgid in ['PROFILE2', 'PROFILE3']:
            self.wait_confirm(msgid)
        action = self.show_choices_message('PROFILE_ASK', ('PROFILE_POS', None, True),
                                           ('PROFILE_NEG', None, False)).wait()
        if action.future.result():
            for msgid in ['PROFILE_CHANGENAME1', 'PROFILE_CHANGENAME2',
                          'PROFILE_CHANGENAME3', 'PROFILE_CHANGENAME4']:
                self.wait_confirm(msgid)
        return self.step_last

    def step_last(self):
        self.wait_confirm('END1')
        self.wait_confirm('END2')
        self._clubhouse_state.characters_disabled = False
        return self.step_complete_and_stop
