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


class Story_Riley2(Quest):

    __tags__ = ['pathway:web', 'skillset:Narrative', 'difficulty:easy',
                'skillset:LaunchQuests', 'skillset:felix']
    __pathway_order__ = 55
    __is_narrative__ = True

    QUESTION_MESSAGES = []

    def setup(self):
        self._info_messages = self.get_loop_messages('STORY_RILEY2')

    def step_begin(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id in self.QUESTION_MESSAGES:
            action = self.show_choices_message(message_id,
                                               ('NOQUEST_POSITIVE', None, True),
                                               ('NOQUEST_NEGATIVE', None, False),
                                               narrative=True).wait()
            suffix = '_RPOS' if action.future.result() else '_RNEG'
            self.show_confirm_message(message_id + suffix, narrative=True).wait()

        else:
            self.wait_confirm(message_id, narrative=True)

        if message_id == self._info_messages[-1]:
            return self.step_complete_and_stop

        return self.step_begin, message_index + 1

    def step_complete_and_stop(self):
        self.dismiss_message(narrative=True)
        super().step_complete_and_stop()
