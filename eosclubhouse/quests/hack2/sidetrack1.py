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


class Sidetrack1(Quest):

    __app_id__ = 'com.hack_computer.Sidetrack'
    __app_common_install_name__ = 'SIDETRACK'
    __tags__ = ['pathway:games', 'difficulty:easy', 'skillset:LaunchQuests']
    __pathway_order__ = 100

    MIN_LEVEL = 1
    MAX_LEVEL = 23

    def setup(self):
        self.confirmed_messages = []
        self.cutscene_played = False

    def _reset_confirmed_messages(self):
        self.confirmed_messages = []

    def _get_unconfirmed_message(self, message_id_list):
        for message_id in message_id_list:
            if message_id not in self.confirmed_messages:
                return message_id
        return None

    def step_begin(self):
        self.ask_for_app_launch(message_id='LAUNCH_ADA')

        highest_achieved_level = self.app.get_js_property('highestAchievedLevel')

        # @fixme: This is a workaround to https://phabricator.endlessm.com/T29180
        # Sometimes Sidetrack app takes lot of time to start and get_js_property times out.
        if highest_achieved_level is None:
            logger.debug('Quest %s: Cannot get \'highestAchievedLevel\' for %s. Trying again...',
                         self.get_id(), self.app.dbus_name)
            return self.step_begin

        self.app.set_js_property('availableLevels', ('u', self.MAX_LEVEL))
        self._reset_confirmed_messages()
        return self.step_play_level, False

    @Quest.with_app_launched()
    def step_play_level(self, level_changed, level_succeed=None):
        current_level = self.app.get_js_property('currentLevel')

        # @fixme: This is a workaround to https://phabricator.endlessm.com/T29180
        # Sometimes Sidetrack app takes lot of time to start and get_js_property times out.
        if current_level is None:
            logger.debug('Quest %s: Cannot get \'current_level\' for %s. Trying again...',
                         self.get_id(), self.app.dbus_name)
            return self.step_play_level, level_changed, level_succeed

        message_id = None
        # messages_to_confirm = []
        # hint_message = None
        if current_level == 1:
            if level_succeed is False:
                message_id = self._get_unconfirmed_message(['DIED_RESTART'])
            else:
                message_id = self._get_unconfirmed_message([
                    'ASSIGNMENT_ADA', 'ASSIGNMENT_RILEY', 'ASSIGNMENT_FABER',
                    'ASSIGNMENT_STUDENT', 'ASSIGNMENT_ESTELLE',
                    'ASSIGNMENT_SANIEL', 'MANUAL1_INTRO'
                ])
                if message_id is None:
                    self.show_hints_message('MANUAL1')
        elif current_level == 2:
            message_id = self._get_unconfirmed_message(['MANUAL2'])
        elif current_level == 3:
            message_id = self._get_unconfirmed_message(['MANUAL3'])
        elif current_level == 4:
            message_id = self._get_unconfirmed_message(['MANUAL4', 'MANUAL5'])
        elif current_level == 6:
            message_id = self._get_unconfirmed_message(['MANUAL6', 'MANUAL7'])
        elif current_level == 7:
            message_id = self._get_unconfirmed_message(['ROBOTS1', 'ROBOTS2'])
            if message_id is None:
                self.show_hints_message('ROBOTS3')
        elif current_level == 10:
            message_id = self._get_unconfirmed_message(['MOREROBOTS'])
        elif current_level == 13:
            message_id = self._get_unconfirmed_message(['AUTO1'])
        elif current_level == 14:
            if not self.cutscene_played:
                # felix destroys the controls here
                self.app.set_js_property('controlsCutscene', ('b', True))
                self.pause(1)
                self.wait_for_app_js_props_changed(self.app, ['controlsCutscene'], timeout=20)
                self.cutscene_played = True
            message_id = self._get_unconfirmed_message([
                'AUTO1_FELIX', 'AUTO1_FABER',
                'AUTO1_ADA', 'AUTO1_PLOT', 'AUTO1_ESTELLE_REACTION',
            ])
            if message_id is None:
                self.show_hints_message('AUTO1_RILEY')
        elif current_level == 15:
            message_id = self._get_unconfirmed_message(['AUTO2_INTRO'])
            if message_id is None:
                self.show_hints_message('AUTO2')
        elif current_level == 16:
            if level_changed:
                self.show_hints_message('AUTO3')
            elif level_succeed is False:
                message_id = self._get_unconfirmed_message(['AUTO3_FAILURE'])
        elif current_level == 17:
            message_id = self._get_unconfirmed_message([
                'AUTO3_SUCCESS', 'AUTO4_SANIEL', 'AUTO4_RILEY'
            ])
        elif current_level == 18:
            message_id = self._get_unconfirmed_message(['ONEJUMP_PRE', 'ONEJUMP'])
            if message_id is None:
                self.show_hints_message('ONEJUMP_ADA')
        elif current_level == 19:
            message_id = self._get_unconfirmed_message(['ONEFORWARD'])
            if message_id is None:
                self.show_hints_message('ONEFORWARD_ADA')
        elif current_level == 20:
            message_id = self._get_unconfirmed_message(['SLIDING'])
        elif current_level == 21:
            message_id = self._get_unconfirmed_message(['WASTEJUMPS'])
        elif current_level == 22:
            message_id = self._get_unconfirmed_message([
                'DRAMA_ADA', 'DRAMA_FABER'
            ])
        elif current_level == self.MAX_LEVEL:
            return self.last_level
        else:
            self.dismiss_message()

        actions = [self.connect_app_js_props_changes(self.app, ['currentLevel', 'success'])]
        if message_id is not None:
            actions.append(self.show_confirm_message(message_id))

        self.wait_for_one(actions)

        level_changed = False
        level_succeed = None
        if self.confirmed_step():
            self.confirmed_messages.append(message_id)
        elif current_level != self.app.get_js_property('currentLevel', 1):
            level_changed = True
            self._reset_confirmed_messages()
        else:
            # Current level hasn't changed, so either the player
            # completed the level or died:
            level_succeed = self.app.get_js_property('success', False)

        return self.step_play_level, level_changed, level_succeed

    @Quest.with_app_launched()
    def last_level(self):
        self.wait_confirm('AUTO5')
        self.show_hints_message('AUTO5_ADA')
        # wait for the player to die, as they cannot pass this level
        self.wait_for_app_js_props_changed(self.app, ['success'])
        self.wait_confirm('AUTO5_FAILURE_SANIEL')
        self.wait_confirm('AUTO5_FAILURE_SANIEL2')
        self.wait_confirm('AUTO5_FAILURE_ADA')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        return self.step_complete_and_stop
