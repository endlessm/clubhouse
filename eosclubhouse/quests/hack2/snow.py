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
from eosclubhouse.system import App, Desktop


class Snow(Quest):

    __EXTENSION__ = 'snow@endlessos.org'
    __APP__ = 'org.gnome.Extensions'

    __tags__ = ['pathway:operating system', 'difficulty:medium', 'since:2.0', 'require:network']

    def setup(self):
        self._installing = False
        self._installed = False
        # Not using __app_id__ to avoid the installation check, we'll install
        # during the quest
        self._app = App(self.__APP__)

    def step_begin(self):
        action = self.show_choices_message('HELLO1', ('NOQUEST_POSITIVE', None, True),
                                           ('NOQUEST_NEGATIVE', None, False)).wait()
        if action.future.result():
            return self.step_install_extension
        else:
            return self.step_abort

    def step_install_extension(self):
        for message_id in ['EXTENSION1', 'EXTENSION2', 'EXTENSION3']:
            self.wait_confirm(message_id)

        info = Desktop.get_extension_info(self.__EXTENSION__)
        if 'state' not in info:

            self._installing = True
            self._installed = False

            def callback(value):
                self._installing = False
                self._installed = value

            self.show_message('EXTENSION4')
            # not installed let's try to install
            Desktop.install_extension(self.__EXTENSION__, callback)

            # active wait until the extension is installed or fail
            while self._installing:
                self.pause(1)

            if not self._installed:
                # Can't install the extension, so we can't continue
                self.wait_confirm('EXTENSION_ERROR')
                return self.step_abort()

        return self.step_install_extensions_app

    def step_install_extensions_app(self):
        if not self._app.is_installed():
            self.wait_confirm('EXTENSION_APP1')
            self.wait_for_app_install(confirm=False)

        return self.step_enable_disable

    def step_enable_disable(self):
        self.ask_for_app_launch(app=self._app, message_id='ENABLE1')

        for message_id in ['ENABLE2', 'ENABLE3']:
            self.wait_confirm(message_id)

        # wait for the snow extension to be enabled
        info = Desktop.get_extension_info(self.__EXTENSION__)
        while info.get('state', 0) != 1:
            self.pause(1)
            info = Desktop.get_extension_info(self.__EXTENSION__)

        for message_id in ['ENABLE4', 'ENABLE5']:
            self.wait_confirm(message_id)

        return self.step_extensions_toolbox

    def step_extensions_toolbox(self):
        self.wait_confirm('TOOLBOX1')
        self.wait_for_app_in_foreground(app=self._app)
        self._app.pulse_flip_to_hack_button(True)
        self.wait_confirm('TOOLBOX2')
        self._app.pulse_flip_to_hack_button(False)
        self.wait_confirm('TOOLBOX3')

        return self.step_unicode

    def step_unicode(self):
        for message_id in ['UNICODE1', 'UNICODE2', 'UNICODE3']:
            self.wait_confirm(message_id)
        return self.step_styles

    def step_styles(self):
        messages = [
            'STYLES1',
            'STYLES2',
            'STYLES3',
            'STYLES4',
            'STYLES5',
            'STYLES6',
        ]
        for message_id in messages:
            self.wait_confirm(message_id)

        self.wait_confirm('END')

        return self.step_complete_and_stop()
