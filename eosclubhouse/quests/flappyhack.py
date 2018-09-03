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

from eosclubhouse.quest import Registry, Quest


class FlappyHack(Quest):

    def __init__(self):
        super().__init__('FlappyBird Hacking', 'aggretsuko',
                         ('Betcha cannot beat my super high score in the FlappyHack game! '
                          'Wanna try it?'))

    def _opened_already(self):
        print('OPENED')

    def _not_opened_already(self):
        print('NOT OPENED')

    def start(self):
        self.show_message('Then make sure that you open FlappyHack!')
        self.show_message('Bring it on!!!!!', mood='mad')
        self.show_question('Have you opened it yet?',
                           choices=[('Yup', self._opened_already),
                                    ('Not yet…', self._not_opened_already)])


Registry.register_quest(FlappyHack)
