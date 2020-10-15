# Copyright (C) 2020 Endless OS Foundation LLC.
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

import logging

from gi.repository import Gio


_logger = logging.getLogger(__name__)


class NetworkManager:
    @classmethod
    def is_connected(klass):
        monitor = Gio.NetworkMonitor.get_default()
        return monitor.get_connectivity() == Gio.NetworkConnectivity.FULL

    @classmethod
    def is_limited(klass):
        monitor = Gio.NetworkMonitor.get_default()
        return monitor.get_connectivity() == Gio.NetworkConnectivity.LIMITED

    @classmethod
    def connect_connection_change(klass, callback):
        monitor = Gio.NetworkMonitor.get_default()

        def _network_changed_cb(*args):
            callback()

        return monitor.connect('network-changed', _network_changed_cb)

    @classmethod
    def disconnect_connection_change(klass, handler):
        monitor = Gio.NetworkMonitor.get_default()
        monitor.disconnect(handler)
