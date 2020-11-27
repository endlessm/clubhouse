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
from eosclubhouse.system import GameStateService


class System_Tour(Quest):

    __app_id__ = 'com.hack_computer.OperatingSystemApp'
    __app_common_install_name__ = 'SYSTEM'
    __tags__ = ['pathway:operating system', 'difficulty:easy', 'skillset:LaunchQuests']
    __pathway_order__ = 100

    def setup(self):
        self._gss = GameStateService()

    def step_begin(self):
        self.wait_confirm('GREET1')
        # don't bother with keys, just unlock everything
        for lockNumber in range(1, 4):
            self._gss.set('lock.OperatingSystemApp.' + str(lockNumber), {'locked': False})
        return self.step_launch

    def step_launch(self):
        self.ask_for_app_launch()
        return self.step_app_running

    @Quest.with_app_launched()
    def step_app_running(self):
        self.wait_confirm('STUFFTODO')
        self.wait_for_app_js_props_changed(props=['flipped'])
        self.wait_confirm('FLIPPEDSTUFF')
        return self.step_complete_and_stop
