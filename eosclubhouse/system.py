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

from eosclubhouse import logger
from gi.repository import GLib, GObject, Gio


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

    _shell_app_store_proxy = Gio.DBusProxy.new_sync(SESSION_BUS, 0, None,
                                                    'org.gnome.Shell',
                                                    '/org/gnome/Shell',
                                                    'org.gnome.Shell.AppStore',
                                                    None)

    _shell_proxy = Gio.DBusProxy.new_sync(SESSION_BUS, 0, None,
                                          'org.gnome.Shell',
                                          '/org/gnome/Shell',
                                          'org.gnome.Shell',
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
            klass._app_launcher_proxy.Launch('(su)', name, int(time.time()))
        except GLib.Error as e:
            print(e)
            return False
        return True

    @classmethod
    def show_app_grid(klass):
        try:
            # @todo: Call a direct method in the Shell interface when that's available
            klass._shell_proxy.Eval('(s)', 'Main.overview.showApps();')
        except GLib.Error as e:
            print(e)
            return False
        return True

    @classmethod
    def add_app_to_grid(klass, app_name):
        if not app_name.endswith('.desktop'):
            app_name += '.desktop'

        try:
            klass._shell_app_store_proxy.AddApplication('(s)', app_name)
        except GLib.Error as e:
            print(e)
            return False
        return True

    @classmethod
    def remove_app_from_grid(klass, app_name):
        if not app_name.endswith('.desktop'):
            app_name += '.desktop'

        try:
            klass._shell_app_store_proxy.RemoveApplication('(s)', app_name)
        except GLib.Error as e:
            print(e)
            return False
        return True


class App:

    def __init__(self, app_dbus_name):
        self._clippy = Gio.DBusProxy.new_sync(Desktop.SESSION_BUS, 0, None,
                                              app_dbus_name,
                                              '/com/endlessm/Clippy',
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

    def highlight_object(self, obj, timestamp=None):
        stamp = timestamp or int(time.time())
        self._clippy.Highlight('(su)', obj, stamp)


class GameStateService(GObject.GObject):

    __gsignals__ = {
        'changed': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
    }

    _proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                            0,
                                            None,
                                            'com.endlessm.GameStateService',
                                            '/com/endlessm/GameStateService',
                                            'com.endlessm.GameStateService',
                                            None)

    # @todo: This is becoming a proxy of a proxy, so we should try to use a
    # more direct later
    def __init__(self):
        super().__init__()

        self._proxy.connect('g-signal', self._g_signal_cb)

    def _g_signal_cb(self, proxy, sender_name, signal_name, params):
        if signal_name == 'changed':
            self.emit('changed')

    def set(self, key, variant):
        self._proxy.Set('(sv)', key, variant)

    def get(self, key):
        try:
            return self._proxy.Get('(s)', key)
        except GLib.Error as e:
            # Raise errors unless they are the expected (key missing)
            if not self._is_key_error(e):
                raise

    @staticmethod
    def _is_key_error(error):
        return Gio.DBusError.get_remote_error(error) == 'com.endlessm.GameStateService.KeyError'


class SoundPlayer:

    _proxy = None

    @classmethod
    def play(class_, sound_event_id, result_handler=None, user_data=None):
        """
        Plays a sound asynchronously.
        By default, it "fires and forgets": no return value.

        Args:
            sound_event_id (str): The sound event id to play.

        Optional keyword arguments:
            result_handler: A function that is invoked when the async call
                finishes. The function's arguments are the following:
                proxy_object, result and user_data.
            data: The user data passed to the result_handler function.
        """
        class_._play(sound_event_id, result_handler=result_handler,
                     user_data=user_data)

    @classmethod
    def play_sync(class_, sound_event_id):
        """
        Plays a sound synchronously.

        Args:
            sound_event_id (str): The sound event id to play.

        Returns:
            str: The uuid of the new played sound.
        """
        return class_._play(sound_event_id, async=False)

    @classmethod
    def _play(class_, sound_event_id, async=True, result_handler=None, user_data=None):
        if result_handler is None:
            result_handler = class_._black_hole
        try:
            if async:
                class_.get_proxy().PlaySound("(s)", sound_event_id,
                                             result_handler=result_handler,
                                             user_data=user_data)
            else:
                return class_.get_proxy().PlaySound("(s)", sound_event_id)
        except GLib.Error as err:
            logger.error("Error playing sound '%s'" % sound_event_id)

    @classmethod
    def stop(class_, uuid, result_handler=None, user_data=None):
        """
        Stops a sound asynchronously.

        Args:
            uuid (str): The sound uuid to stop playing.

        Optional keyword arguments:
            result_handler: A function that is invoked when the async call
                finishes. The function's arguments are the following:
                proxy_object, result and user_data.
            data: The user data passed to the result_handler function.
        """
        if result_handler is None:
            result_handler = class_._black_hole
        try:
            class_.get_proxy().StopSound("(s)", uuid, result_handler=result_handler,
                                         user_data=user_data)
        except GLib.Error as err:
            logger.error("Error stopping sound '%s'" % uuid)

    @classmethod
    def _black_hole(_class, _proxy, _result, user_data=None):
        pass

    @classmethod
    def get_proxy(class_):
        if not class_._proxy:
            class_._proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                           0,
                                                           None,
                                                           'com.endlessm.HackSoundServer',
                                                           '/com/endlessm/HackSoundServer',
                                                           'com.endlessm.HackSoundServer',
                                                           None)
        return class_._proxy
