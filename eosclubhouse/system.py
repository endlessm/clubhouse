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

import configparser
import gi
import json
gi.require_version('Json', '1.0')
import os
import shutil
import time

from eosclubhouse import logger
from eosclubhouse.config import DATA_DIR
from eosclubhouse.hackapps import HackableAppsManager
from eosclubhouse.soundserver import HackSoundServer
from eosclubhouse.utils import get_flatpak_sandbox
from gi.repository import GLib, GObject, Gio, Json


class Desktop:

    SETTINGS_HACK_MODE_KEY = 'hack-mode-enabled'
    HACK_BACKGROUND = 'file://{}/share/backgrounds/Desktop-BGs-Beta-Sketch_Blue.png'\
        .format(get_flatpak_sandbox())

    HACK_CURSOR = 'cursor-glitchy'

    # Apps ids to override flatpak GTK3_MODULES with libclippy
    CLIPPY_APPS = [
        'com.endlessm.dinosaurs.en',
        'com.endlessm.encyclopedia.en',
        'com.endlessm.Fizzics',
        'com.endlessm.Hackdex_chapter_one',
        'com.endlessm.Hackdex_chapter_two',
        'com.endlessm.LightSpeed',
        'com.endlessm.OperatingSystemApp',
        'com.endlessm.Sidetrack',
    ]

    _dbus_proxy = None
    _app_launcher_proxy = None
    _shell_app_store_proxy = None
    _shell_proxy = None
    _shell_settings = None

    @classmethod
    def get_dbus_proxy(klass):
        if klass._dbus_proxy is None:
            klass._dbus_proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                               0,
                                                               None,
                                                               'org.freedesktop.DBus',
                                                               '/org/freedesktop/DBus',
                                                               'org.freedesktop.DBus',
                                                               None)
        return klass._dbus_proxy

    @classmethod
    def get_app_launcher_proxy(klass):
        if klass._app_launcher_proxy is None:
            klass._app_launcher_proxy = \
                Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                               0,
                                               None,
                                               'org.gnome.Shell',
                                               '/org/gnome/Shell',
                                               'org.gnome.Shell.AppLauncher',
                                               None)

        return klass._app_launcher_proxy

    @classmethod
    def get_shell_app_store_proxy(klass):
        if klass._shell_app_store_proxy is None:
            klass._shell_app_store_proxy = \
                Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                               0,
                                               None,
                                               'org.gnome.Shell',
                                               '/org/gnome/Shell',
                                               'org.gnome.Shell.AppStore',
                                               None)

        return klass._shell_app_store_proxy

    @classmethod
    def get_shell_proxy(klass):
        if klass._shell_proxy is None:
            klass._shell_proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                                0,
                                                                None,
                                                                'org.gnome.Shell',
                                                                '/org/gnome/Shell',
                                                                'org.gnome.Shell',
                                                                None)

        return klass._shell_proxy

    @classmethod
    def get_shell_proxy_async(klass, callback, *callback_args):
        def _on_shell_proxy_ready(proxy, result):
            try:
                klass._shell_proxy = proxy.new_finish(result)
            except GLib.Error as e:
                logger.warning("Error: Failed to get Shell proxy:", e.message)
                return

            callback(klass._shell_proxy, *callback_args)

        if klass._shell_proxy is None:
            Gio.DBusProxy.new_for_bus(Gio.BusType.SESSION,
                                      0,
                                      None,
                                      'org.gnome.Shell',
                                      '/org/gnome/Shell',
                                      'org.gnome.Shell',
                                      None,
                                      _on_shell_proxy_ready)
        else:
            callback(klass._shell_proxy, *callback_args)

    @classmethod
    def get_app_desktop_name(_klass, app_name):
        if app_name.endswith('.desktop'):
            return app_name
        return app_name + '.desktop'

    @classmethod
    def app_is_running(klass, name):
        try:
            klass.get_dbus_proxy().GetNameOwner('(s)', name)
        except GLib.Error:
            return False
        return True

    @classmethod
    def launch_app(klass, name):
        try:
            klass.get_app_launcher_proxy().Launch('(su)', name, int(time.time()))
        except GLib.Error as e:
            logger.error(e)
            return False
        return True

    @classmethod
    def focus_app(klass, app_name):
        app_name = klass.get_app_desktop_name(app_name)

        try:
            klass.get_shell_proxy().FocusApp('(s)', app_name)
        except GLib.Error as e:
            logger.error(e)
            return False
        return True

    @classmethod
    def is_app_in_grid(klass, app_name):
        app_name = klass.get_app_desktop_name(app_name)
        try:
            apps = klass.get_shell_app_store_proxy().ListApplications()
            return app_name in apps
        except GLib.Error as e:
            logger.error(e)
        return False

    @classmethod
    def add_app_to_grid(klass, app_name):
        app_name = klass.get_app_desktop_name(app_name)

        try:
            klass.get_shell_app_store_proxy().AddApplication('(s)', app_name)
        except GLib.Error as e:
            logger.error(e)
            return False
        return True

    @classmethod
    def remove_app_from_grid(klass, app_name):
        app_name = klass.get_app_desktop_name(app_name)

        try:
            klass.get_shell_app_store_proxy().RemoveApplication('(s)', app_name)
        except GLib.Error as e:
            logger.error(e)
            return False
        return True

    @classmethod
    def is_app_in_foreground(klass, app_name):
        app_name = klass.get_app_desktop_name(app_name)

        try:
            prop = klass.get_shell_proxy().get_cached_property('FocusedApp')
            if prop is not None:
                return prop.unpack() == app_name
        except GLib.Error as e:
            logger.error(e)
        return False

    @classmethod
    def connect_app_in_foreground_change(klass, app_in_foreground_cb, *args):
        def _props_changed_cb(_proxy, changed_properties,
                              _invalidated, app_in_foreground_cb, *args):
            changed_properties_dict = changed_properties.unpack()
            app_in_foreground = changed_properties_dict.get('FocusedApp')
            if app_in_foreground is not None:
                app_in_foreground_cb(app_in_foreground, *args)

        shell_proxy = klass.get_shell_proxy()
        return shell_proxy.connect('g-properties-changed', _props_changed_cb,
                                   app_in_foreground_cb, *args)

    @classmethod
    def disconnect_app_in_foreground_change(klass, handler_id):
        shell_proxy = klass.get_shell_proxy()
        return shell_proxy.disconnect(handler_id)

    @classmethod
    def get_shell_settings(klass):
        if klass._shell_settings is None:
            klass._shell_settings = Gio.Settings('org.gnome.shell')

        return klass._shell_settings

    @classmethod
    def set_hack_background(klass, enabled):
        ''' This changes the background to the Hack one '''

        desktop = Gio.Settings('org.gnome.desktop.background')
        clubhouse = Gio.Settings('com.endlessm.clubhouse')

        old_picture_uri = desktop.get_string('picture-uri')
        if enabled:
            new_picture_uri = \
                clubhouse.get_string('hack-mode-enabled-picture-uri') or klass.HACK_BACKGROUND
        else:
            new_picture_uri = clubhouse.get_string('hack-mode-disabled-picture-uri')

        if new_picture_uri:
            desktop.set_string('picture-uri', new_picture_uri)
        else:
            desktop.reset('picture-uri')

        if old_picture_uri:
            if enabled:
                clubhouse.set_string('hack-mode-disabled-picture-uri', old_picture_uri)
            else:
                clubhouse.set_string('hack-mode-enabled-picture-uri', old_picture_uri)

    @classmethod
    def ensure_hack_cursor_is_present(klass):
        src = f'{DATA_DIR}/cursors/cursor-glitchy.xmc'
        dirname = '~/.icons/cursor-glitchy/cursors/'
        dirname = os.path.expanduser(dirname)
        cursor = os.path.join(dirname, 'left_ptr')
        theme = os.path.join(dirname, 'index.theme')

        if os.path.exists(cursor):
            return

        os.makedirs(dirname, exist_ok=True)
        shutil.copy2(src, cursor)
        config = configparser.ConfigParser()
        config.add_section('Icon Theme')
        config.set('Icon Theme', 'Inherits', 'Adwaita')

        with open(theme, 'w') as f:
            config.write(f)

    @classmethod
    def set_hack_cursor(klass, enabled):
        ''' This changes the cursor to the Hack one '''

        klass.ensure_hack_cursor_is_present()

        interface = Gio.Settings('org.gnome.desktop.interface')

        if enabled:
            interface.set_string('cursor-theme', klass.HACK_CURSOR)
        else:
            interface.reset('cursor-theme')

    @classmethod
    def get_hack_mode(klass):
        return klass.get_shell_settings().get_boolean(klass.SETTINGS_HACK_MODE_KEY)

    @classmethod
    def set_hack_mode(klass, enabled):
        # Override clippy apps
        for name in klass.CLIPPY_APPS:
            App(name).enable_clippy(enabled)

        return klass.get_shell_settings().set_boolean(klass.SETTINGS_HACK_MODE_KEY, enabled)


class App:

    APP_JS_PARAMS = 'view.JSContext.globalParameters'

    _clippy = None
    _gtk_app_proxy = None
    _gtk_actions_proxy = None
    _gtk_launch_app_proxy = None

    def __init__(self, app_dbus_name, app_dbus_path=None):
        self._app_dbus_name = app_dbus_name
        self._app_dbus_path = app_dbus_path or ('/' + app_dbus_name.replace('.', '/'))

    @property
    def dbus_name(self):
        return self._app_dbus_name

    def get_clippy_proxy(self):
        if self._clippy is None:
            self._clippy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                          0,
                                                          None,
                                                          self._app_dbus_name,
                                                          '/com/endlessm/Clippy',
                                                          'com.endlessm.Clippy',
                                                          None)

        return self._clippy

    def get_gtk_app_proxy(self):
        if self._gtk_app_proxy is None:
            self._gtk_app_proxy = \
                Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                               Gio.DBusProxyFlags.DO_NOT_AUTO_START |
                                               Gio.DBusProxyFlags.DO_NOT_AUTO_START_AT_CONSTRUCTION,
                                               None,
                                               self._app_dbus_name,
                                               self._app_dbus_path,
                                               'org.gtk.Application',
                                               None)

        return self._gtk_app_proxy

    def get_gtk_actions_proxy(self):
        if self._gtk_actions_proxy is None:
            self._gtk_actions_proxy = \
                Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                               Gio.DBusProxyFlags.DO_NOT_AUTO_START |
                                               Gio.DBusProxyFlags.DO_NOT_AUTO_START_AT_CONSTRUCTION,
                                               None,
                                               self._app_dbus_name,
                                               self._app_dbus_path,
                                               'org.gtk.Actions',
                                               None)

        return self._gtk_actions_proxy

    def get_gtk_launch_app_proxy(self):
        if self._gtk_launch_app_proxy is None:
            self._gtk_launch_app_proxy = \
                Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                               Gio.DBusProxyFlags.DO_NOT_AUTO_START_AT_CONSTRUCTION,
                                               None,
                                               self._app_dbus_name,
                                               self._app_dbus_path,
                                               'org.gtk.Application',
                                               None)

        return self._gtk_launch_app_proxy

    def is_running(self):
        return self.get_gtk_app_proxy().props.g_name_owner is not None

    def get_object_property(self, obj, prop):
        return self.get_clippy_proxy().Get('(ss)', obj, prop)

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

        return self.get_clippy_proxy().Set('(ssv)', obj, prop, variant)

    def get_js_property(self, prop, default_value=None):
        value = default_value

        try:
            value = self.get_object_property(self.APP_JS_PARAMS, prop)
        except Exception as e:
            logger.error(e)

        return value

    def set_js_property(self, prop, value):
        try:
            self.set_object_property(self.APP_JS_PARAMS, prop, value)
        except Exception as e:
            logger.error(e)
            return False

        return True

    def connect_props_change(self, obj, props, property_changed_cb, *args):
        obj = obj or self.APP_JS_PARAMS
        return [self.connect_object_props_change(obj, props,
                                                 property_changed_cb, *args)]

    def connect_object_props_change(self, obj, props, js_property_changed_cb, *args):
        # Check if the properties really changed, because in older versions of
        # Clippy, it was notifying always, instead of only if the value of the
        # property had changed.
        # @todo: Remove once it's safe for our users to use this logic without this
        # safeguard.
        values = {}
        for prop in props:
            values[prop] = self.get_js_property(prop)

        def _props_changed_cb(_proxy, _owner, signal_name, params, props, js_property_changed_cb,
                              *args):
            if signal_name != 'ObjectNotify':
                return

            _notify_obj, notify_prop, value = params.unpack()

            if notify_prop in props and value != values[notify_prop]:
                logger.debug('Property %s changed from %s to %s', notify_prop,
                             values[notify_prop], value)
                values[notify_prop] = value
                js_property_changed_cb(*args)

        for prop in props:
            self.get_clippy_proxy().Connect('(sss)', obj, 'notify', prop)

        proxy = self.get_clippy_proxy()
        return proxy.connect('g-signal', _props_changed_cb, props, js_property_changed_cb, *args)

    def disconnect_object_props_change(self, handler_id):
        self.get_clippy_proxy().disconnect(handler_id)

    def connect_running_change(self, app_running_changed_cb, *args):
        def _name_owner_changed(proxy, _pspec, app_running_changed_cb, *args):
            app_running_changed_cb(*args)

        proxy = self.get_gtk_app_proxy()
        return proxy.connect('notify::g-name-owner', _name_owner_changed, app_running_changed_cb,
                             *args)

    def disconnect_running_change(self, handler_id):
        self.get_gtk_app_proxy().disconnect(handler_id)

    def highlight_object(self, obj, timestamp=None):
        stamp = timestamp or int(time.time())
        self.get_clippy_proxy().Highlight('(su)', obj, stamp)

    def launch(self):
        if not Desktop.launch_app(self.dbus_name):
            return self.launch_gapp()
        return True

    def launch_gapp(self):
        try:
            self.get_gtk_launch_app_proxy().Activate('(a{sv})', [])
        except GLib.Error as e:
            logger.error(e)
            return False
        return True

    def pulse_flip_to_hack_button(self, enable):
        app = HackableAppsManager.get_hackable_app(self._app_dbus_name)
        if app:
            app.pulse_flip_to_hack_button(enable)

    def enable_clippy(self, enable=True):
        sandbox = get_flatpak_sandbox()
        filesystems = f'{sandbox}:ro;~/.icons;'
        clippy = f'{sandbox}/clippy/lib/libclippy-module.so'

        filename = f'~/.local/share/flatpak/overrides/{self.dbus_name}'
        filename = os.path.expanduser(filename)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.mkdir(dirname)

        config = configparser.ConfigParser()
        if os.path.exists(filename):
            config.read(filename)

        options = {
            ('Context', 'filesystems'): filesystems,
            ('Session Bus Policy', 'com.endlessm.HackSoundServer'): 'talk',
            ('Environment', 'GTK3_MODULES'): clippy,
        }

        if enable:
            for key, value in options.items():
                section, option = key
                if not config.has_section(section):
                    config.add_section(section)
                config.set(section, option, value)
        else:
            for section, option in options:
                if config.has_option(section, option):
                    config.remove_option(section, option)

        with open(filename, 'w') as f:
            config.write(f)


class GameStateService(GObject.GObject):

    __gsignals__ = {
        'changed': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
    }

    _proxy = None

    @classmethod
    def _get_gss_proxy(klass):
        if klass._proxy is None:
            klass._proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                          0,
                                                          None,
                                                          'com.endlessm.GameStateService',
                                                          '/com/endlessm/GameStateService',
                                                          'com.endlessm.GameStateService',
                                                          None)

        return klass._proxy

    # @todo: This is becoming a proxy of a proxy, so we should try to use a
    # more direct later
    def __init__(self):
        super().__init__()

        self._get_gss_proxy().connect('g-signal', self._g_signal_cb)

    def _g_signal_cb(self, proxy, sender_name, signal_name, params):
        if signal_name == 'changed':
            self.emit('changed')

    def _convert_variant_arg(self, variant):
        # If we're passing a dictionary instead, then we just convert it from json
        if isinstance(variant, dict):
            try:
                json_str = json.dumps(variant)
                variant = Json.gvariant_deserialize_data(json_str, -1, None)
            except Exception:
                raise TypeError('Error setting GSS entry: value is not a variant nor can it be '
                                'converted to json')
        return variant

    def set(self, key, variant):
        variant = self._convert_variant_arg(variant)
        self._get_gss_proxy().Set('(sv)', key, variant)

    def set_async(self, key, variant):
        variant = self._convert_variant_arg(variant)

        def _on_set_done_callback(proxy, result):
            try:
                proxy.call_finish(result)
            except GLib.Error as e:
                logger.error('Error calling set_async on GSS: %s', e.message)

        self._get_gss_proxy().call('Set', GLib.Variant('(sv)', (key, variant)),
                                   Gio.DBusCallFlags.NONE, -1, None, _on_set_done_callback)

    def get(self, key, value_if_missing=None):
        try:
            return self._get_gss_proxy().Get('(s)', key)
        except GLib.Error as e:
            # Raise errors unless they are the expected (key missing)
            if not self._is_key_error(e):
                raise
        return value_if_missing

    def update(self, key, new_value, value_if_missing=None):
        state = self.get(key, value_if_missing)
        if isinstance(state, dict) and isinstance(new_value, dict):
            state.update(new_value)
        else:
            state = new_value
        self.set(key, state)

    def reset(self):
        return self._get_gss_proxy().Reset()

    @staticmethod
    def _is_key_error(error):
        return Gio.DBusError.get_remote_error(error) == 'com.endlessm.GameStateService.KeyError'


class ToolBoxTopic(GObject.GObject):

    _INTERFACE_NAME = 'com.endlessm.HackToolbox.Topic'
    _PATH_TEMPLATE = '/com/endlessm/HackToolbox/window/{}/topic/{}'
    _proxy = None
    _properties_proxy = None

    @classmethod
    def _build_dbus_path(klass, app_name, topic_name):
        return klass._PATH_TEMPLATE.format(app_name.replace('.', '_'),
                                           topic_name)

    def _get_proxy(self):
        if self._proxy is None:
            self._proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                         0,
                                                         None,
                                                         'com.endlessm.HackToolbox',
                                                         self._dbus_path,
                                                         self._INTERFACE_NAME,
                                                         None)

        return self._proxy

    def _get_properties_proxy(self):
        if self._properties_proxy is None:
            self._properties_proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                0,
                None,
                'com.endlessm.HackToolbox',
                self._dbus_path,
                'org.freedesktop.DBus.Properties',
                None,
            )

        return self._properties_proxy

    def __init__(self, app_name, topic_name):
        super().__init__()
        self._app_name = app_name
        self._topic_name = topic_name
        self._dbus_path = self._build_dbus_path(app_name, topic_name)

    def reveal(self, reveal=True):
        self._get_proxy().reveal('(b)', GLib.Variant('b', reveal))

    def connect_clicked(self, on_clicked_cb, *args):

        def _clicked_cb(_proxy, _owner, signal_name, params, on_clicked_cb, *args):
            if signal_name != 'clicked':
                return

            on_clicked_cb(self._app_name, self._topic_name, *args)

        return self._get_proxy().connect('g-signal', _clicked_cb, on_clicked_cb, *args)

    def disconnect_clicked(self, handler_id):
        self._get_proxy().disconnect(handler_id)

    def get_sensitive(self):
        variant = GLib.Variant('(ss)', (self._INTERFACE_NAME, 'sensitive'))
        sensitive = self._get_properties_proxy().call_sync('Get', variant,
                                                           Gio.DBusCallFlags.NONE, -1, None)
        if sensitive is None:
            logger.warning("Failed to get 'sensitive' property"
                           " from toolbox topic %s", self._dbus_path)

        return sensitive is not None and sensitive.unpack()[0]

    def set_sensitive(self, sensitive=True):
        variant = GLib.Variant('(ssv)', (self._INTERFACE_NAME, 'sensitive',
                                         GLib.Variant('b', sensitive)))
        return self._get_properties_proxy().call_sync('Set', variant,
                                                      Gio.DBusCallFlags.NONE, -1, None)


# Allow to import the HackSoundServer from the system while using a more friendly name
Sound = HackSoundServer
