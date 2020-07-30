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

import logging

from gi.repository import Gio
from gi.repository import GLib
from gi.repository import GObject

logger = logging.getLogger(__name__)


class HackableApp(GObject.Object):
    _BUS_NAME = 'com.hack_computer.HackableAppsManager'
    _INTERFACE_NAME = 'com.hack_computer.HackableApp'

    def __init__(self, object_path):
        super().__init__()
        self.object_path = object_path
        self._proxy = Gio.DBusProxy.new_for_bus_sync(
            Gio.BusType.SESSION,
            0,
            None,
            'com.hack_computer.HackableAppsManager',
            self.object_path,
            self._INTERFACE_NAME,
            None
        )
        self._properties_proxy = None

    def get_proxy(self):
        return self._proxy

    def get_properties_proxy(self):
        if self._properties_proxy is None:
            self._properties_proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                0,
                None,
                'org.gnome.Shell',
                self.object_path,
                'org.freedesktop.DBus.Properties',
                None,
            )
        return self._properties_proxy

    def _get_app_id(self):
        try:
            variant = self.get_proxy().get_cached_property('AppId')
            if variant:
                return variant.unpack()
        except GLib.Error as e:
            logger.error(e)
        return None

    def _get_toolbox_visible(self):
        try:
            return self.get_proxy().get_cached_property('ToolboxVisible')
        except GLib.Error as e:
            logger.error(e)
        return None

    def _set_toolbox_visible(self, value):
        try:
            variant = GLib.Variant('(ssv)', (self._INTERFACE_NAME,
                                             'ToolboxVisible',
                                             GLib.Variant('b', value)))
            self.get_properties_proxy().call_sync('Set', variant,
                                                  Gio.DBusCallFlags.NONE, -1,
                                                  None)
        except GLib.Error as e:
            logger.error(e)
            return False
        return True

    def _get_pulse_flip_to_hack_button(self):
        try:
            variant = GLib.Variant('(ss)', (self._INTERFACE_NAME, 'PulseFlipToHackButton'))
            return self.get_properties_proxy().call_sync('Get', variant,
                                                         Gio.DBusCallFlags.NONE, -1, None)
        except GLib.Error as e:
            logger.error(e)
        return None

    def _set_pulse_flip_to_hack_button(self, value):
        try:
            variant = GLib.Variant('(ssv)', (self._INTERFACE_NAME,
                                             'PulseFlipToHackButton',
                                             GLib.Variant('b', value)))
            self.get_properties_proxy().call_sync('Set', variant,
                                                  Gio.DBusCallFlags.NONE, -1,
                                                  None)
        except GLib.Error as e:
            logger.error(e)
            return False
        return True

    toolbox_visible = \
        GObject.Property(getter=_get_toolbox_visible,
                         setter=_set_toolbox_visible,
                         type=object,
                         flags=GObject.ParamFlags.READWRITE)

    app_id = \
        GObject.Property(getter=_get_app_id, type=str,
                         flags=GObject.ParamFlags.READABLE)

    pulse_flip_to_hack_button = \
        GObject.Property(getter=_get_pulse_flip_to_hack_button,
                         setter=_set_pulse_flip_to_hack_button,
                         type=object,
                         flags=GObject.ParamFlags.READWRITE)


class HackableAppsManager:

    _INTERFACE_NAME = 'com.hack_computer.HackableAppsManager'
    _DBUS_PATH = '/' + _INTERFACE_NAME.replace('.', '/')
    _proxy = None
    _properties_proxy = None

    @classmethod
    def get_proxy(klass):
        if klass._proxy is None:
            klass._proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                0,
                None,
                klass._INTERFACE_NAME,
                klass._DBUS_PATH,
                klass._INTERFACE_NAME,
                None
            )

        return klass._proxy

    @classmethod
    def get_properties_proxy(klass):
        if klass._properties_proxy is None:
            klass._properties_proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                0,
                None,
                klass._INTERFACE_NAME,
                klass._DBUS_PATH,
                'org.freedesktop.DBus.Properties',
                None,
            )
        return klass._properties_proxy

    @classmethod
    def _currently_hackable_apps(klass):
        variant = GLib.Variant('(ss)', (klass._INTERFACE_NAME, 'CurrentlyHackableApps'))
        hackable_apps = klass.get_properties_proxy().call_sync(
            'Get', variant, Gio.DBusCallFlags.NONE, -1, None)

        if not hackable_apps:
            return None

        return hackable_apps.unpack()[0]

    @classmethod
    def get_hackable_app(klass, app_id):
        """
        Gets a HackableApp object.

        Args:
            app_id(str): Application id of the hackable application.
        """
        try:
            for object_path in klass._currently_hackable_apps():
                hackable_app = HackableApp(object_path)
                if hackable_app.app_id == app_id:
                    return hackable_app
        except GLib.Error as e:
            logger.error(e)
        return None
