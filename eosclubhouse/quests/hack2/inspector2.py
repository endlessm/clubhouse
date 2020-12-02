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


class Inspector2(Quest):

    __tags__ = ['pathway:web', 'difficulty:medium', 'require:network']
    __pathway_order__ = 582

    def setup(self):
        self._info_messages = self.get_loop_messages('INSPECTOR2', start=2)

    def step_begin(self):
        self.wait_confirm('1')
        return self.step_launch

    def step_launch(self):
        if self.is_cancelled():
            return self.step_abort()

        self.deploy_file('Inspector/base.css',
                         '~/Documents/WebSources/InspectorQuest/', override=True)
        self.deploy_file('Inspector/index.html',
                         '~/Documents/WebSources/InspectorQuest/', override=True)
        self.deploy_file('Inspector/cats.html',
                         '~/Documents/WebSources/InspectorQuest/', override=True)
        self.deploy_file('Inspector/nyancat.html',
                         '~/Documents/WebSources/InspectorQuest/', override=True)
        self.deploy_file('Inspector/nyancat.mp3',
                         '~/Documents/WebSources/InspectorQuest/', override=True)
        self.deploy_file('Inspector/img/morse.png',
                         '~/Documents/WebSources/InspectorQuest/img/', override=True)
        self.deploy_file('Inspector/img/biel-morro-unsplash.jpg',
                         '~/Documents/WebSources/InspectorQuest/img/', override=True)
        self.deploy_file('Inspector/img/alexander-london-unsplash.jpg',
                         '~/Documents/WebSources/InspectorQuest/img/', override=True)
        self.deploy_file('Inspector/img/markus-spiske-unsplash-cropped.jpg',
                         '~/Documents/WebSources/InspectorQuest/img/', override=True)
        self.deploy_file('Inspector/img/thomas-kelley-unsplash-cropped.jpg',
                         '~/Documents/WebSources/InspectorQuest/img/', override=True)
        self.deploy_file('Inspector/img/kimberly-farmer-unsplash-cropped.jpg',
                         '~/Documents/WebSources/InspectorQuest/img/', override=True)
        self.deploy_file('Inspector/img/nyancat.webp',
                         '~/Documents/WebSources/InspectorQuest/img/', override=True)

        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="Woohoo!")
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
