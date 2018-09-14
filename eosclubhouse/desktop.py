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

from gi.repository import GLib, Gio


class Desktop:

    SESSION_BUS = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    _dbus_proxy = Gio.DBusProxy.new_sync(SESSION_BUS, 0, None,
                                         'org.freedesktop.DBus',
                                         '/org/freedesktop/DBus',
                                         'org.freedesktop.DBus',
                                         None)
    _app_launcher_proxy = Gio.DBusProxy.new_sync(SESSION_BUS, 0, None,
                                                 'org.gnome.Shell',
                                                 '/org/gnome/Shell',
                                                 'org.gnome.Shell.AppLauncher',
                                                 None)

    @classmethod
    def app_is_running(klass, name):
        try:
            klass._dbus_proxy.GetNameOwner('(s)', name)
        except GLib.Error as e:
            print(e)
            return False
        return True

    @classmethod
    def launch_app(klass, name):
        try:
            klass._app_launcher_proxy.Launch('(su)', name, time.time())
        except GLib.Error as e:
            print(e)
            return False
        return True


class App:

    def __init__(self, app_dbus_name):
        app_path = '/' + str(app_dbus_name).replace('.', '/')
        self._clippy = Gio.DBusProxy.new_sync(Desktop.SESSION_BUS, 0, None,
                                              app_dbus_name,
                                              app_path,
                                              'com.endlessm.Clippy',
                                              None)

    def get_clippy_proxy(self):
        return self._clippy

    def get_object_property(self, obj, prop):
        return self._clippy.Get('(ss)', obj, prop)

    def set_object_property(self, obj, prop, value):
        '''Sets a property in an object of the app.

        The value argument can be a GLib.Variant, or, for convenience, a string (will create
        a string type GLib.Variant), or a tuple expressing the type and value of the variant
        e.g. ('u', 42). Needless to say, the value set should be expected type for the given
        property.

        This means this method can be called as e.g.:
          app_instance.set_object_property('obj-name', 'some-string-prop', 'my string')
          app_instance.set_object_property('obj-name', 'some-string-prop', ('s', 'my string'))

          app_instance.set_object_property('obj-name', 'some-boolean-prop', True)

          app_instance.set_object_property('obj-name', 'some-list-of-uints-prop', ('au', [1,2,3]))

          app_instance.set_object_property('obj-name', 'some-list-of-uints-prop',
                                           GLib.Variant('au', [1,2,3]))
        '''

        if isinstance(value, tuple):
            variant = GLib.Variant(value[0], value[1])
        elif isinstance(value, str):
            variant = GLib.Variant('s', value)
        elif isinstance(value, bool):
            variant = GLib.Variant('b', value)
        else:
            variant = value

        return self._clippy.Set('(ssv)', obj, prop, variant)

    def highlight_object(self, obj):
        self._clippy.Highlight('(s)', obj)
