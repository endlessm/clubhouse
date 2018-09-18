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

import time

from eosclubhouse.libquest import Registry, Quest, QuestSet
from eosclubhouse.desktop import Desktop, App


class FlappyHack(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.hackybird'

    def __init__(self):
        super().__init__('FlappyBird Hacking', 'aggretsuko',
                         ('Betcha cannot beat my score in Hackybird! '
                          'My friend Aggretsuko will help!'
                          'Wanna try it?'))

    def _open_app(self):
        Desktop.launch_app(self.TARGET_APP_DBUS_NAME)

    def start(self):
        self.show_message("Then make sure that you open Hackybird! Let's do it!!!!!", mood='happy')
        time.sleep(2)

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            self.show_question("Hmm… I don't see Hackybird running… Should open it for you?",
                               choices=[('Please do!', self._open_app)])
            while not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                time.sleep(1)

        app = App(self.TARGET_APP_DBUS_NAME)

        score = 1
        self.show_message("Okay… Now try to beat my super mega awesome score of… "
                          "{} POINT!".format(score), mood='in_love')
        app.set_object_property('label_name', 'label', 'Aggretsuko')
        app.set_object_property('label_score', 'label', str(score))
        app.set_object_property('stack_app', 'visible-child-name', 'page0')
        app.set_object_property('view_hack', 'score', ('i', score))
        app.highlight_object('button_start')

        attempts = 0
        while True:
            current_score = app.get_object_property('view_hack', 'score')
            print('Attempts:', attempts, current_score)
            if current_score > score:
                if score == 100:
                    self.show_message("Oh no! You beat me…! Good for you…", mood='angry_sad')
                    break

                self.show_message("Oh WHAT!? … You think you beat me? Check this out!", mood='mad')
                time.sleep(2)

                score = 100
                app.set_object_property('label_name', 'label', 'Aggretsuko')
                app.set_object_property('label_score', 'label', str(score))
                app.set_object_property('stack_app', 'visible-child-name', 'page0')
                self.show_message("WAH-HAHAHA! Now try again…", mood='mad')
                time.sleep(2)
            elif attempts == 10:
                self.show_message("You just have to do {} point…".format(score), mood='in_love')
            attempts += 1
            time.sleep(1)


class GamesQuestSet(QuestSet):

    __character_id__ = 'fenneko'
    __quests__ = [FlappyHack]


Registry.register_quest_set(GamesQuestSet)
