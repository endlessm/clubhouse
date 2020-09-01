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

from gi.repository import GLib, Gio
from eosclubhouse.utils import convert_variant_arg


_logger = logging.getLogger(__name__)


class tour_meta(type):
    @property
    def propagateEvents(cls):
        return cls.get_prop('PropagateEvents')

    @propagateEvents.setter
    def propagateEvents(cls, value):
        cls.set_prop('PropagateEvents', value)

    @property
    def skippable(cls):
        return cls.get_prop('Skippable')

    @skippable.setter
    def skippable(cls, value):
        cls.set_prop('Skippable', value)


class TourServer(metaclass=tour_meta):

    _proxy = None
    _properties_proxy = None
    _DBUS_PATH = '/com/endlessm/onboarding'
    _DBUS_ID = 'com.endlessm.onboarding'
    _CALL_TIMEOUT = 20_000

    @classmethod
    def _get_proxy(klass):
        if klass._proxy is None:
            klass._proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
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
                Gio.BusType.SESSION,
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
    def set_prop(klass, key, value):
        variant = convert_variant_arg(value)
        return klass._get_properties_proxy().Set('(ssv)', klass._DBUS_ID, key, variant)

    @classmethod
    def _call_method(klass, method, *args, callback=None):
        variant = None
        if args:
            variant_type = '('
            for arg in args:
                if isinstance(arg, bool):
                    variant_type += 'b'
                    continue
                if isinstance(arg, str):
                    variant_type += 's'
                    continue
                if isinstance(arg, int):
                    variant_type += 'u'
                    continue
                if isinstance(arg, float):
                    variant_type += 'd'
                    continue
            variant_type += ')'
            variant = GLib.Variant(variant_type, args)

        def _on_done(proxy, result):
            ret = None
            try:
                ret = proxy.call_finish(result).unpack()[0]
            except GLib.Error as e:
                _logger.error('Error calling HighlightRect on tour: %s', e.message)

            if callback:
                callback(ret)

        klass._get_proxy().call(
            method, variant, Gio.DBusCallFlags.NONE, klass._CALL_TIMEOUT, None, _on_done)

    @classmethod
    def highlight_rect(klass, x, y, width, height, text='', callback=None):
        klass._call_method('HighlightRect', x, y, width, height, text, callback=callback)

    @classmethod
    def highlight_circle(klass, x, y, radius, text='', callback=None):
        klass._call_method('HighlightCircle', x, y, radius, text, callback=callback)

    @classmethod
    def highlight_widget(klass, name, text='', callback=None):
        klass._call_method('HighlightWidget', name, text, callback=callback)

    @classmethod
    def highlight_icon(klass, app_id, text='', callback=None):
        klass._call_method('HighlightDesktopIcon', app_id, text, callback=callback)

    @classmethod
    def highlight_fuzzy(klass, position='center', size='20%', shape='rect', text='', callback=None):
        klass._call_method('HighlightFuzzy', position, size, shape, text, callback=callback)

    @classmethod
    def show_overview(klass, show, callback=None):
        klass._call_method('ShowOverview', show, callback=callback)

    @classmethod
    def clean(klass, callback=None):
        klass._call_method('Clean', callback=callback)
