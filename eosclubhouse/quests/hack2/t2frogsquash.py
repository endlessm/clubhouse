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


class T2FrogSquash(Quest):

    __app_id__ = 'com.endlessnetwork.frogsquash'
    __tags__ = ['pathway:games', 'difficulty:easy', 'skillset:LaunchQuests']
    __pathway_order__ = 125

    def step_begin(self):
        return self.step_check_intro

    def step_check_intro(self):
        if self.get_named_quest_conf('T2Intro', 'has_seen_intro'):
            return self.step_normalrun
        else:
            return self.step_firstrun

    def step_firstrun(self):
        self.wait_confirm('FIRSTRUN1')
        self.wait_confirm('FIRSTRUN2')
        self.set_conf('has_seen_intro', True)
        self.save_conf()
        self.wait_confirm('FIRSTRUN3', confirm_label='OK, got it.')
        return self.step_normalrun

    def step_normalrun(self):
        self.wait_confirm('GREET1')
        self.wait_confirm('GREET2', confirm_label='Will do!')
        self.wait_confirm('BYE')
        return self.step_launch

    def step_launch(self):
        self.app.launch()
        self.wait_for_app_in_foreground()
        self.wait_for_app_in_foreground(in_foreground=False)
        return self.step_complete_and_stop
