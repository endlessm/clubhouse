# Copyright (C) 2018 Endless Mobile, Inc.
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
# Authors:
#       Joaquim Rocha <jrocha@endlessm.com>
#

import os
import time

from eosclubhouse.libquest import Registry, Quest, QuestSet
from eosclubhouse.desktop import Desktop, App
from gi.repository import GLib


class GEditHack(Quest):

    TARGET_APP_DBUS_NAME = 'org.gnome.gedit'

    def __init__(self):
        super().__init__('GEdit Hacking', 'aggretsuko',
                         ('Betcha cannot write anything in Gedit! '
                          'Wanna try it?'))
        if self.get_conf('complete'):
            self._initial_msg = 'I see you tried this already! Wanna go again?'

    def _open_app(self):
        Desktop.launch_app(self.TARGET_APP_DBUS_NAME)

    def _add_app_to_desktop(self):
        Desktop.remove_app_from_grid(self.TARGET_APP_DBUS_NAME)
        Desktop.add_app_to_grid(self.TARGET_APP_DBUS_NAME)
        Desktop.show_app_grid()
        self.show_message('There you go! Now click the GEdit icon!')

    def on_key_event(self, event):
        print(event.keyval)

    def start(self):
        self.set_keyboard_request(True)
        self.show_message('Then make sure that you open Gedit! Bring it on!!!!!', mood='mad')
        time.sleep(2)

        self.show_question("Hmm… I don't see Gedit running… Should open it for you?",
                           choices=[('Please do!', self._open_app),
                                    ('Give me the app!', self._add_app_to_desktop)])
        while not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            if self.is_cancelled():
                return
            time.sleep(1)

        txt = 'I love Aggretsuko!'
        self.show_message("Awesome! Now write '{}' in the editor. I'll wait…".format(txt),
                          mood='in_love')

        app = App(self.TARGET_APP_DBUS_NAME)

        attempts = 0
        success = False
        while True:
            if self.is_cancelled():
                return

            current_text = app.get_object_property('view.buffer', 'text')
            print('Attempts:', attempts, current_text)
            if current_text.lower() == txt.lower():
                success = True
                break
            elif len(current_text) == 0 and attempts == 3:
                app.highlight_object('view')
            elif attempts == 10:
                self.show_message("You just have to write: {}".format(txt), mood='angry_sad')
            elif attempts > 20:
                break
            attempts += 1
            time.sleep(1)

        if success:
            self.show_message("Awesome! You're the best! A cookie for you!", mood='happy')
            self.set_conf('complete', True)
        else:
            self.show_message("Oh well… Maybe next time…", mood='disappointed')


class Aggretsuko(QuestSet):

    __character_id__ = 'aggretsuko'
    __quests__ = [GEditHack()]
    __position__ = (50, 400)

    def __init__(self):
        super().__init__()
        self.props.visible = 'CLUBHOUSE_SHOW_SAMPLE_QUESTS' in os.environ
        GLib.timeout_add_seconds(10, self._highlight_on_timeout)

    def _highlight_on_timeout(self):
        self.nudge()
        return GLib.SOURCE_REMOVE


Registry.register_quest_set(Aggretsuko)
