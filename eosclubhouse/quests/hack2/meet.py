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
from eosclubhouse.libquest import InkQuest


class Meet(InkQuest):

    __app_id__ = 'com.hack_computer.Sidetrack'

    __tags__ = ['pathway:games', 'difficulty:easy']
    __pathway_order__ = 10
    __ink_quest_id__ = 'test'
    # __ink_quest_id__ = 'p5-quest'
    # __ink_quest_id__ = 'TheIntercept'
