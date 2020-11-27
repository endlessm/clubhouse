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


class LMMSQuest1(Quest):

    __app_id__ = 'io.lmms.LMMS'
    __app_common_install_name__ = 'LMMS'
    __tags__ = ['pathway:art', 'difficulty:medium', 'since:1.4', 'require:network']
    __pathway_order__ = 615

    def setup(self):
        self._info_messages = self.get_loop_messages('LMMSQUEST1')

    def step_begin(self):
        return self.step_launch

    def step_launch(self):
        self.wait_confirm('GREET')
        if self.is_cancelled():
            return self.step_abort()

        self.app.launch()
        self.open_url_in_browser('https://www.youtube.com/watch?v=DWzRtBS1dYI')
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="You bet!")
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
