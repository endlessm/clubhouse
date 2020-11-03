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


class MakerSketch(Quest):

    ARTICLE_NAME = 'Makers_Sketch_Prototype_Challenge'

    __tags__ = ['pathway:maker', 'difficulty:easy', 'skillset:LaunchQuests']
    __pathway_order__ = 220

    def step_begin(self):
        self.wait_confirm('WELCOME', confirm_label='Sounds interesting!')
        if self.is_cancelled():
            return self.step_abort()
        self.open_pdf(self.ARTICLE_NAME)
        return self.step_complete_and_stop
