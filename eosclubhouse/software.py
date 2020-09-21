# Copyright (C) 2020 Endless OS Foundation LLC
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
#       Daniel Garcia <danigm@endlessos.org>


from eosclubhouse import logger
from gi.repository import Gio, GLib


class GnomeSoftware:
    _proxy = None

    @classmethod
    def get_proxy(klass):
        if klass._proxy is None:
            klass._proxy = \
                Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                               Gio.DBusProxyFlags.DO_NOT_AUTO_START |
                                               Gio.DBusProxyFlags.DO_NOT_AUTO_START_AT_CONSTRUCTION,
                                               None,
                                               'org.gnome.Software',
                                               '/org/gnome/Software',
                                               'org.gtk.Actions',
                                               None)
        return klass._proxy

    @classmethod
    def details(klass, app_id):
        def _on_done_callback(proxy, result):
            try:
                proxy.call_finish(result)
            except GLib.Error as e:
                logger.error('Error showing details of app: %s', e.message)

        args = GLib.Variant('(ss)', (app_id, ''))
        variant = GLib.Variant('(sava{sv})', ['details', [args], None])
        klass.get_proxy().call('Activate', variant,
                               Gio.DBusCallFlags.NONE, -1, None, _on_done_callback)
