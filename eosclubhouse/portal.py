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

from gi.repository import Gio, GLib


_logger = logging.getLogger(__name__)


class Portal:
    _proxy = None
    _response_signal_id = None

    @classmethod
    def _get_proxy(klass):
        if klass._proxy is None:
            klass._proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                0,
                None,
                'org.freedesktop.portal.Desktop',
                '/org/freedesktop/portal/desktop',
                'org.freedesktop.portal.Background',
                None
            )
        return klass._proxy

    @classmethod
    def request_background(klass, message='', callback=None):
        handle_token = 'clubhouse_req_hack'
        try:
            klass._connect_response(handle_token, callback)
            proxy = klass._get_proxy()
            options = {
                'handle_token': GLib.Variant('s', handle_token),
            }
            if message:
                options['reason'] = GLib.Variant('s', message)
            proxy.RequestBackground('(sa{sv})', '', options)
        except GLib.Error as err:
            _logger.warning('Error requesting background permission to portal: %s', err)

    @classmethod
    def _connect_response(klass, token, callback):
        proxy = klass._get_proxy()
        connection = proxy.get_connection()

        sender = connection.get_unique_name()[1:].replace('.', '_')
        handle = f'/org/freedesktop/portal/desktop/request/{sender}/{token}'

        if klass._response_signal_id:
            klass._disconnect_response()

        def _response_received(conn, sender_name, object_path, interface_name,
                               signal_name, parameters, user_data):
            if parameters:
                _id, params = parameters.unpack()
                if callback:
                    callback(params['background'])

        klass._response_signal_id = Gio.DBusConnection.signal_subscribe(
            connection,
            'org.freedesktop.portal.Desktop',
            'org.freedesktop.portal.Request',
            'Response',
            handle,
            None,
            Gio.DBusSignalFlags.NO_MATCH_RULE,
            _response_received,
            None,
        )

    @classmethod
    def _disconnect_response(klass):
        proxy = klass._get_proxy()
        connection = proxy.get_connection()
        Gio.DBusConnection.signal_unsubscribe(connection,
                                              klass._response_signal_id)
