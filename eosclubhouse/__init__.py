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

import logging
import os

DEBUG_ENV_VARS = {'CLUBHOUSE_LOG_LEVEL': 'debug',
                  'GTK_DEBUG': 'interactive',
                  'G_MESSAGES_DEBUG': 'all'}

log_level = logging.INFO

for key, value in DEBUG_ENV_VARS.items():
    if os.environ.get(key, None) == value:
        log_level = logging.DEBUG
        break

logging.basicConfig(level=log_level)
logger = logging.getLogger(__name__)
