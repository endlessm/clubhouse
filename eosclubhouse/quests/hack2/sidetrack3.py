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
from eosclubhouse import logger


class Sidetrack3(Quest):

    __app_id__ = 'com.hack_computer.Sidetrack'
    __app_common_install_name__ = 'SIDETRACK'
    __available_after_completing_quests__ = ['Sidetrack2']
    __tags__ = ['pathway:games', 'difficulty:medium', 'skillset:LaunchQuests', 'since:1.6']
    __pathway_order__ = 102

    def setup(self):
        self.confirmed_messages = []

    def _reset_confirmed_messages(self):
        self.confirmed_messages = []

    def _get_unconfirmed_message(self, message_id_list):
        for message_id in message_id_list:
            if message_id not in self.confirmed_messages:
                return message_id
        return None

    def step_begin(self):
        self.ask_for_app_launch(message_id='LAUNCH')

        highest_level = self._app.get_js_property('highestAchievedLevel')

        # @fixme: This is a workaround to https://phabricator.endlessm.com/T29180
        # Sometimes Sidetrack app takes lot of time to start and get_js_property times out.
        if highest_level is None:
            logger.debug('Quest %s: Cannot get \'highestAchievedLevel\' for %s. Trying again...',
                         self.get_id(), self.app.dbus_name)
            return self.step_begin

        # This is a workaround to wait until the sidetrack app reads the
        # information from the game state service. In the future we should add
        # a signal or a property to the toyapps and move this wait to a new
        # method in Quest
        current_level = int(self._app.get_js_property('currentLevel'))
        while current_level == 0:
            logger.debug('Current level is 0, waiting for sidetrack to load data')
            self.pause(1)
            current_level = self._app.get_js_property('currentLevel')

        if highest_level > 36:
            self._app.set_js_property('highestAchievedLevel', ('u', 28))
        self._app.set_js_property('availableLevels', ('u', 36))
        self._reset_confirmed_messages()
        return self.step_play_level, False

    @Quest.with_app_launched()
    def step_play_level(self, level_changed, level_success=None):
        current_level = self._app.get_js_property('currentLevel')
        message_id = None
        if current_level == 28:
            self.wait_confirm('INTRO1')
            self.show_hints_message('INTRO2')
            return self.step_level28, False, False, False
        elif current_level == 29:
            self.dismiss_message()
            self.show_hints_message('LEVEL_29')
        elif current_level == 30:
            self.dismiss_message()
            message_id = self._get_unconfirmed_message(['LEVEL_30_INTRO'])
            if message_id is None:
                self.show_hints_message('LEVEL_30')
        elif current_level == 31:
            self.dismiss_message()
            message_id = self._get_unconfirmed_message(['LEVEL_31_ADA',
                                                        'LEVEL_31_FABER',
                                                        'LEVEL_31_ESTELLE'])
        elif current_level == 34:
            self.dismiss_message()
            message_id = self._get_unconfirmed_message(['LEVEL_34_FABER',
                                                        'LEVEL_34_ESTELLE',
                                                        'LEVEL_34_FABER_2'])
        elif current_level == 35:
            self.dismiss_message()
            message_id = self._get_unconfirmed_message(['LEVEL_35'])
        elif current_level == 36:
            return self.step_lastlevel
        else:
            self.dismiss_message()

        actions = [self.connect_app_js_props_changes(self._app, ['currentLevel', 'success'])]
        if message_id is not None:
            actions.append(self.show_confirm_message(message_id))

        self.wait_for_one(actions)

        level_changed = False
        level_success = None
        if self.confirmed_step():
            self.confirmed_messages.append(message_id)
        elif current_level != self._app.get_js_property('currentLevel'):
            level_changed = True
            self._reset_confirmed_messages()
        else:
            # Current level hasn't changed, so either the player
            # completed the level or died:
            level_success = self._app.get_js_property('success')

        return self.step_play_level, level_changed, level_success

    @Quest.with_app_launched()
    def step_level28(self, level28_changed, level28_success, level28_flipped):
        if level28_changed:  # or level28_success:
            return self.step_play_level, level28_changed, level28_success
        if level28_flipped:
            self.show_hints_message('PUSH')

        level28_actions = [self.connect_app_js_props_changes(self._app, ['currentLevel',
                                                                         'success', 'flipped'])]
        self.wait_for_one(level28_actions)
        level28_changed = False
        level28_success = None
        level28_flipped = False
        if self._app.get_js_property('currentLevel') != 28:
            level28_changed = True
        else:
            # Current level hasn't changed, so either the player
            # completed the level or died:
            level28_success = self._app.get_js_property('success')
        if self._app.get_js_property('flipped'):
            level28_flipped = True
        return self.step_level28, level28_changed, level28_success, level28_flipped

    @Quest.with_app_launched()
    def step_lastlevel(self):
        for msg_id in ['LEVEL_36_ADA', 'LEVEL_36_SANIEL', 'LEVEL_36_ADA_2']:
            self.wait_confirm(msg_id)
        self.wait_for_app_js_props_changed(self._app, ['success'])
        for msg_id in ['UNBEATABLE_FABER', 'UNBEATABLE_SANIEL', 'UNBEATABLE_RILEY']:
            self.wait_confirm(msg_id)
        return self.step_success

    def step_success(self):
        return self.step_complete_and_stop
