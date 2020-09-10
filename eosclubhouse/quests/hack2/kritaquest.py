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


class KritaQuest(Quest):

    __app_id__ = 'org.kde.krita'
    __tags__ = ['pathway:art', 'difficulty:medium', 'skillset:LaunchQuests']
    __pathway_order__ = 200

    def setup(self):
        self._info_messages = self.get_loop_messages('INFO')

    def step_begin(self):

        if not self.has_connection():
            self.wait_confirm('NOQUEST_NOCONNECTION')
            return self.step_abort

        if not self.app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='Got it!')
            return self.step_abort

        self.wait_confirm('LAUNCH')
        self.app.launch()
        self.pause(4)
        return self.step_info_loop

    def step_info_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        options = [
            ('NOQUEST_NAV_BAK', None, -1),
            ('NOQUEST_NAV_FWD', None, 1),
        ]

        if message_id == self._info_messages[-1]:
            options.append(('QUIT', None, 0))

        action = self.show_choices_message(message_id, *options).wait()

        chosen_action = action.future.result()

        if chosen_action == 0:
            self.wait_confirm('BYE', confirm_label='See you later!')
            return self.step_complete_and_stop
        else:
            return self.step_info_loop, message_index + chosen_action
