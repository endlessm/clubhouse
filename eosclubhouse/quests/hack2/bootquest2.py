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


class BootQuest2(Quest):

    __app_id__ = 'com.sublimetext.three'
    __tags__ = ['pathway:web', 'difficulty:medium', 'since:1.8']
    __pathway_order__ = 615

    def setup(self):
        self._info_messages = self.get_loop_messages('BOOTQUEST2', start=3)

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='Got it!')
            return self.step_abort

        self.wait_confirm('1')
        self.wait_confirm('2')
        self.deploy_file('Bootstrap2Quest/images/dog.jpg',
                         '~/Documents/myproject/images/', override=True)
        self.deploy_file('Bootstrap2Quest/images/cats.jpg',
                         '~/Documents/myproject/images/', override=True)
        self.deploy_file('Bootstrap2Quest/images/bird.jpg',
                         '~/Documents/myproject/images/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap.css',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap.css.map',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap.min.css',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap.min.css.map',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap-grid.css',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap-grid.css.map',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap-grid.min.css',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap-grid.min.css.map',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap-reboot.css',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap-reboot.css.map',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap-reboot.min.css',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/css/bootstrap-reboot.min.css.map',
                         '~/Documents/myproject/css/', override=True)
        self.deploy_file('Bootstrap2Quest/js/bootstrap.bundle.js',
                         '~/Documents/myproject/js', override=True)
        self.deploy_file('Bootstrap2Quest/js/bootstrap.bundle.js.map',
                         '~/Documents/myproject/js', override=True)
        self.deploy_file('Bootstrap2Quest/js/bootstrap.bundle.min.js',
                         '~/Documents/myproject/js', override=True)
        self.deploy_file('Bootstrap2Quest/js/bootstrap.bundle.min.js.map',
                         '~/Documents/myproject/js', override=True)
        self.deploy_file('Bootstrap2Quest/js/bootstrap.js',
                         '~/Documents/myproject/js', override=True)
        self.deploy_file('Bootstrap2Quest/js/bootstrap.js.map',
                         '~/Documents/myproject/js', override=True)
        self.deploy_file('Bootstrap2Quest/js/bootstrap.min.js',
                         '~/Documents/myproject/js', override=True)
        self.deploy_file('Bootstrap2Quest/js/bootstrap.min.js.map',
                         '~/Documents/myproject/js', override=True)
        self.deploy_file('Bootstrap2Quest/js/jquery-3.4.1.min.js',
                         '~/Documents/myproject/js', override=True)
        self.deploy_file('Bootstrap2Quest/index.html',
                         '~/Documents/myproject', override=True)
        return self.step_main_loop

    def step_main_loop(self, message_index=0):
        message_id = self._info_messages[message_index]

        if message_id == self._info_messages[-1]:
            self.wait_confirm(message_id, confirm_label="Sweet!")
            return self.step_complete_and_stop

        options = []
        if message_id != self._info_messages[0]:
            options.append(('NOQUEST_NAV_BAK', None, -1))

        options.append(('NOQUEST_NAV_FWD', None, 1))

        action = self.show_choices_message(message_id, *options).wait()
        return self.step_main_loop, message_index + action.future.result()
