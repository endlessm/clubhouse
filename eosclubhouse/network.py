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

    _proxy = None
    _properties_proxy = None
    _DBUS_PATH = '/org/freedesktop/NetworkManager'
    _DBUS_ID = 'org.freedesktop.NetworkManager'

    @classmethod
    def _get_proxy(klass):
        if klass._proxy is None:
            klass._proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SYSTEM,
                                                          0,
                                                          None,
                                                          klass._DBUS_ID,
                                                          klass._DBUS_PATH,
                                                          klass._DBUS_ID,
                                                          None)

        return klass._proxy

    @classmethod
    def _get_properties_proxy(klass):
        if klass._properties_proxy is None:
            klass._properties_proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SYSTEM,
                0,
                None,
                klass._DBUS_ID,
                klass._DBUS_PATH,
                'org.freedesktop.DBus.Properties',
                None,
            )

        return klass._properties_proxy

    @classmethod
    def get_prop(klass, key):
        return klass._get_properties_proxy().Get('(ss)', klass._DBUS_ID, key)

    @classmethod
    def is_connected(klass):
        return klass.get_prop('Connectivity') == 4

    @classmethod
    def is_limited(klass):
        return klass.get_prop('Connectivity') == 3

    @classmethod
    def connect_connection_change(klass, callback):
        proxy = klass._get_proxy()

        def _props_changed_cb(_proxy, changed_properties, _invalidated, *args):
            changed_properties_dict = changed_properties.unpack()
            if 'Connectivity' in changed_properties_dict:
                callback()

        return proxy.connect('g-properties-changed', _props_changed_cb)

    @classmethod
    def disconnect_connection_change(klass, handler):
        klass._get_proxy().disconnect(handler)
