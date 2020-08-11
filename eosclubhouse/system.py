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

import configparser
import json
import os
import shutil
import subprocess
import time

from eosclubhouse import logger
from eosclubhouse.config import DATA_DIR
from eosclubhouse.hackapps import HackableAppsManager
from eosclubhouse.soundserver import HackSoundServer, HackSoundItem
from eosclubhouse.utils import convert_variant_arg, get_flatpak_sandbox
from gi.repository import GLib, GObject, Gio


class Desktop:
    _HACK_DBUS = 'com.hack_computer.hack'
    _HACK_OBJECT_PATH = '/com/hack_computer/hack'
    _BLOCK_HACK_PROPS = False

    SETTINGS_HACK_MODE_KEY = 'HackModeEnabled'
    SETTINGS_HACK_ICON_PULSE = 'HackIconPulse'
    HACK_BACKGROUND = 'file://{}/share/backgrounds/Desktop-BGs-Nov-release.jpg'\
        .format(get_flatpak_sandbox())

    HACK_CURSOR = 'cursor-hack'
    HACK_CURSOR_SIZE = 32

    # Apps ids to override flatpak GTK3_MODULES with libclippy
    CLIPPY_APPS = [
        'com.endlessm.dinosaurs.en',
        'com.endlessm.encyclopedia.en',
        'com.hack_computer.Fizzics',
        'com.hack_computer.Hackdex_chapter_one',
        'com.hack_computer.Hackdex_chapter_two',
        'com.hack_computer.LightSpeed',
        'com.hack_computer.OperatingSystemApp',
        'com.hack_computer.Sidetrack',
    ]

    OLD_CLIPPY_APPS = [
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
    _shell_property_proxy = None
    _shell_settings = None
    _shell_schema = None
    _hack_proxy = None
    _hack_property_proxy = None

    # This is needed to work with EOS <= 3.7
    SHELL_SETTINGS_SCHEMA_ID = 'org.gnome.shell'
    SHELL_SETTINGS_HACK_MODE_KEY = 'hack-mode-enabled'
    SHELL_SETTINGS_HACK_ICON_PULSE = 'hack-icon-pulse'
    _settings_signal_handlers = {}

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
    def _get_shell_properties_proxy(klass):
        if klass._shell_property_proxy is None:
            klass._shell_property_proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                0,
                None,
                'org.gnome.Shell',
                '/org/gnome/Shell',
                'org.freedesktop.DBus.Properties',
                None,
            )

        return klass._shell_property_proxy

    @classmethod
    def get_shell_property(klass, prop_name):
        variant = GLib.Variant('(ss)', ('org.gnome.Shell', prop_name))
        value = klass._get_shell_properties_proxy().call_sync('Get', variant,
                                                              Gio.DBusCallFlags.NONE, -1, None)
        if value is None:
            logger.warning(f"Failed to get '{prop_name}' property from  org.gnome.Shell")
            return None
        return value.unpack()[0]

    @classmethod
    def get_shell_version(klass):
        return klass.get_shell_property('ShellVersion')

    @classmethod
    def get_hack_proxy(klass):
        # Fallback to get_shell_proxy for EOS <= 3.7
        if (klass.get_shell_version() < '3.36'):
            return klass.get_shell_proxy()

        if klass._hack_proxy is None:
            klass._hack_proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                               0,
                                                               None,
                                                               klass._HACK_DBUS,
                                                               klass._HACK_OBJECT_PATH,
                                                               klass._HACK_DBUS,
                                                               None)

        return klass._hack_proxy

    @classmethod
    def _get_hack_properties_proxy(klass):
        if klass._hack_property_proxy is None:
            klass._hack_property_proxy = Gio.DBusProxy.new_for_bus_sync(
                Gio.BusType.SESSION,
                0,
                None,
                klass._HACK_DBUS,
                klass._HACK_OBJECT_PATH,
                'org.freedesktop.DBus.Properties',
                None,
            )

        return klass._hack_property_proxy

    @classmethod
    def get_hack_property(klass, prop_name):
        variant = GLib.Variant('(ss)', (klass._HACK_DBUS, prop_name))
        value = klass._get_hack_properties_proxy().call_sync('Get', variant,
                                                             Gio.DBusCallFlags.NONE, -1, None)
        if value is None:
            logger.warning(f"Failed to get '{prop_name}' property"
                           " from  %s", klass._HACK_DBUS)
            return None
        return value.unpack()[0]

    @classmethod
    def set_hack_property(klass, prop_name, value):
        value = convert_variant_arg(value)
        variant = GLib.Variant('(ssv)', (klass._HACK_DBUS, prop_name, value))
        return klass._get_hack_properties_proxy().call_sync('Set', variant,
                                                            Gio.DBusCallFlags.NONE, -1, None)

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
    def minimize_all(klass):
        """
        Minimizes all the windows from the overview.
        """
        try:
            klass.get_hack_proxy().MinimizeAll()
        except GLib.Error as e:
            logger.error(e)
            return False
        return True

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
            prop = klass.get_hack_proxy().get_cached_property('FocusedApp')
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

        shell_proxy = klass.get_hack_proxy()
        return shell_proxy.connect('g-properties-changed', _props_changed_cb,
                                   app_in_foreground_cb, *args)

    @classmethod
    def disconnect_app_in_foreground_change(klass, handler_id):
        shell_proxy = klass.get_hack_proxy()
        return shell_proxy.disconnect(handler_id)

    @classmethod
    def hack_property_connect(klass, prop_name, callback, *args):
        def _props_changed_cb(_proxy, changed_properties, _invalidated, *args):
            if klass._BLOCK_HACK_PROPS:
                return

            changed_properties_dict = changed_properties.unpack()
            if prop_name in changed_properties_dict:
                new_value = changed_properties_dict.get(prop_name)
                callback(new_value, *args)

        shell_proxy = klass.get_hack_proxy()
        return shell_proxy.connect('g-properties-changed', _props_changed_cb, *args)

    # This is needed to work with EOS <= 3.7
    @classmethod
    def shell_settings_bind(klass, key, target_object, target_property,
                            flags=Gio.SettingsBindFlags.DEFAULT):
        settings = klass.get_shell_settings()
        if settings:
            settings.bind(key, target_object, target_property, flags)

    # This is needed to work with EOS <= 3.7
    @classmethod
    def shell_settings_connect(klass, signal_name, callback, *args):
        settings = klass.get_shell_settings()
        if not settings:
            return 0
        handler_id = settings.connect(signal_name, callback, *args)

        # Storing all signals to be able to block
        handlers = klass._settings_signal_handlers.get(signal_name, [])
        handlers.append(handler_id)
        klass._settings_signal_handlers[signal_name] = handlers

        return handler_id

    # This is needed to work with EOS <= 3.7
    @classmethod
    def get_shell_settings(klass):
        if not klass._get_shell_schema():
            klass._shell_settings = None
        elif klass._shell_settings is None:
            klass._shell_settings = Gio.Settings(klass.SHELL_SETTINGS_SCHEMA_ID)

        return klass._shell_settings

    @classmethod
    def _get_shell_schema(klass):
        schema_source = Gio.SettingsSchemaSource.get_default()
        if klass._shell_schema is None:
            klass._shell_schema = schema_source.lookup(klass.SHELL_SETTINGS_SCHEMA_ID, False)
        if klass._shell_schema is None:
            logger.warning('Schema \'%s\' not found.', klass.SHELL_SETTINGS_SCHEMA_ID)
        return klass._shell_schema

    @classmethod
    def set_hack_background(klass, enabled):
        ''' This changes the background to the Hack one

        When enabling the background will be always set to the HACK_BACKGROUND.

        When disabling the background will be reset to the previous one stored
        or if the user changes the background we keep the user custom.
        '''

        desktop = Gio.Settings('org.gnome.desktop.background')
        clubhouse = Gio.Settings('com.hack_computer.clubhouse')

        old_picture_uri = desktop.get_string('picture-uri')
        # Enabling and the background is not the hack background yet
        if enabled and old_picture_uri != klass.HACK_BACKGROUND:
            desktop.set_string('picture-uri', klass.HACK_BACKGROUND)
            clubhouse.set_string('hack-mode-disabled-picture-uri', old_picture_uri)
        # Disabling hack and the background has not been changed
        elif not enabled and old_picture_uri == klass.HACK_BACKGROUND:
            new_picture_uri = clubhouse.get_string('hack-mode-disabled-picture-uri')
            if new_picture_uri:
                desktop.set_string('picture-uri', new_picture_uri)
            else:
                desktop.reset('picture-uri')

    @classmethod
    def ensure_hack_cursor_is_present(klass):
        src = f'{DATA_DIR}/cursors'
        basedir = f'~/.icons/{klass.HACK_CURSOR}'
        basedir = os.path.expanduser(basedir)
        dirname = f'{basedir}/cursors'
        theme = os.path.join(dirname, 'index.theme')

        if os.path.exists(basedir):
            shutil.rmtree(basedir)

        os.makedirs(basedir, exist_ok=True)
        shutil.copytree(src, dirname, symlinks=True)
        config = configparser.ConfigParser()
        config.optionxform = lambda opt: opt
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
            interface.set_int('cursor-size', klass.HACK_CURSOR_SIZE)
        else:
            interface.reset('cursor-theme')
            interface.reset('cursor-size')

    @classmethod
    def get_hack_mode(klass):
        # Compatible with EOS <= 3.7
        if (klass.get_shell_version() < '3.36'):
            shell_settings = klass.get_shell_settings()
            if not shell_settings:
                return False
            return klass.get_shell_settings().get_boolean(klass.SHELL_SETTINGS_HACK_MODE_KEY)

        return klass.get_hack_property(klass.SETTINGS_HACK_MODE_KEY)

    @classmethod
    def set_hack_mode_shell(klass, enabled, avoid_signal=False):
        shell_settings = klass.get_shell_settings()
        if not shell_settings:
            return

        signal_name = f'changed::{klass.SHELL_SETTINGS_HACK_MODE_KEY}'
        if avoid_signal:
            klass._block_setting_signals(signal_name)
        response = shell_settings.set_boolean(klass.SHELL_SETTINGS_HACK_MODE_KEY, enabled)
        if avoid_signal:
            klass._block_setting_signals(signal_name, block=False)

        return response

    @classmethod
    def set_hack_mode(klass, enabled, avoid_signal=False):
        # Override clippy apps
        for name in klass.CLIPPY_APPS:
            App(name).enable_clippy(enabled)

        for name in klass.OLD_CLIPPY_APPS:
            App(name).enable_clippy(enabled, old_clippy=True)

        # Compatible with EOS <= 3.7
        if (klass.get_shell_version() < '3.36'):
            return klass.set_hack_mode_shell(enabled, avoid_signal)

        klass._BLOCK_HACK_PROPS = avoid_signal
        response = klass.set_hack_property(klass.SETTINGS_HACK_MODE_KEY, enabled)
        if avoid_signal:
            klass._BLOCK_HACK_PROPS = False

        return response

    @classmethod
    def set_hack_icon_pulse(klass, enabled):
        # Compatible with EOS <= 3.7
        if (klass.get_shell_version() < '3.36'):
            shell_settings = klass.get_shell_settings()
            if not shell_settings:
                return
            return shell_settings.set_boolean(klass.SHELL_SETTINGS_HACK_ICON_PULSE, enabled)

        return klass.set_hack_property(klass.SETTINGS_HACK_ICON_PULSE, enabled)

    @classmethod
    def _block_setting_signals(klass, signal_name, block=True):
        shell_settings = klass.get_shell_settings()
        for handler in klass._settings_signal_handlers.get(signal_name, []):
            if block:
                GObject.signal_handler_block(shell_settings, handler)
            else:
                GObject.signal_handler_unblock(shell_settings, handler)


class App:

    APP_JS_PARAMS = 'view.JSContext.globalParameters'

    _clippy = None
    _gtk_app_proxy = None
    _gtk_actions_proxy = None
    _gtk_launch_app_proxy = None
    _ekn_search_provider_proxy = None
    _knowledgesearch_proxy = None

    def __init__(self, app_dbus_name, app_dbus_path=None):
        self._app_dbus_name = app_dbus_name
        self._app_dbus_path = app_dbus_path or ('/' + app_dbus_name.replace('.', '/'))

    @property
    def dbus_name(self):
        return self._app_dbus_name

    def _bus_label_unescape(self, bus_label):
        # @todo: This should mimic the function with same name in
        # eos-knowledge-services eks-search-app.c . This
        # implementation only works for names with dots as the only
        # special character.
        return bus_label.replace('.', '_2E')

    def get_clippy_proxy(self):
        if self._clippy is None:
            self._clippy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                          0,
                                                          None,
                                                          self._app_dbus_name,
                                                          '/com/hack_computer/Clippy',
                                                          'com.hack_computer.Clippy',
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

    def get_knowledgesearch_proxy(self):
        if self._knowledgesearch_proxy is None:
            self._knowledgesearch_proxy = \
                Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                               Gio.DBusProxyFlags.DO_NOT_AUTO_START_AT_CONSTRUCTION,
                                               None,
                                               self._app_dbus_name,
                                               self._app_dbus_path,
                                               'com.endlessm.KnowledgeSearch',
                                               None)

        return self._knowledgesearch_proxy

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

    def open_article(self, article_name):
        def _get_ekn_id(article_name):
            search_results = None
            try:
                search_results = self.get_ekn_search_provider_proxy().Query(
                    '(aa{sv})',
                    ({'search-terms': GLib.Variant('s', article_name)},))
            except GLib.Error as e:
                logger.error(e)
                return None

            results_count = search_results[1][0][0]['upper_bound']
            if results_count == 0:
                return None

            for elem in search_results[1][0][1]:
                if elem['title'].lower() == article_name.lower():
                    return elem['id']
            return None

        ekn_id = _get_ekn_id(article_name)
        if ekn_id is None:
            return

        self.get_knowledgesearch_proxy().LoadItem('(ssu)', ekn_id, '', 0)

    def get_ekn_search_provider_proxy(self):
        if self._ekn_search_provider_proxy is None:
            self._ekn_search_provider_proxy = \
                Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                               Gio.DBusProxyFlags.DO_NOT_AUTO_START_AT_CONSTRUCTION,
                                               None,
                                               'com.endlessm.EknServices3.SearchProviderV3',
                                               ('/com/endlessm/EknServices3/SearchProviderV3/' +
                                                self._bus_label_unescape(self._app_dbus_name)),
                                               'com.endlessm.ContentMetadata',
                                               None)

        return self._ekn_search_provider_proxy

    def is_running(self):
        return self.get_gtk_app_proxy().props.g_name_owner is not None

    def is_installed(self):
        '''Check if the app is installed.

        Note: This only works for apps distributed as flatpaks.
        '''
        result = subprocess.run(['/usr/bin/flatpak-spawn', '--host',
                                 'flatpak', 'info', '--show-ref', self.dbus_name])
        return result.returncode == 0

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
            app.pulse_flip_to_hack_button = enable

    def enable_clippy(self, enable=True, old_clippy=False):
        sandbox = get_flatpak_sandbox()
        clippy_sandbox = sandbox.replace('app', 'runtime').replace('Clubhouse', 'Clippy.Extension')

        # If old_clippy is True we'll use the com.endlessm.Clippy.Extension//stable
        # instead of the new one and we'll provide DBUS access to the old sound
        # server too
        hack_sound_server_id = 'com.hack_computer.HackSoundServer'
        if old_clippy:
            hack_sound_server_id = 'com.endlessm.HackSoundServer'
            # replace the flatpak branch to stable
            clippy_sandbox = clippy_sandbox.replace('com.hack_computer', 'com.endlessm')\
                                           .replace('eos3', 'stable')\
                                           .replace('custom', 'stable')\
                                           .replace('master', 'stable')
            sandbox = clippy_sandbox

        filesystems = f'{sandbox}:ro;~/.icons;'
        clippy = f'{clippy_sandbox}/lib/libclippy-module.so'

        filename = f'~/.local/share/flatpak/overrides/{self.dbus_name}'
        filename = os.path.expanduser(filename)
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.mkdir(dirname)

        config = configparser.ConfigParser()
        config.optionxform = lambda opt: opt
        if os.path.exists(filename):
            config.read(filename)

        options = {
            ('Context', 'filesystems'): filesystems,
            ('Session Bus Policy', hack_sound_server_id): 'talk',
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
    _DBUS_PATH = '/com/hack_computer/GameStateService'
    _DBUS_ID = 'com.hack_computer.GameStateService'

    @classmethod
    def _get_gss_proxy(klass):
        if klass._proxy is None:
            klass._proxy = Gio.DBusProxy.new_for_bus_sync(Gio.BusType.SESSION,
                                                          0,
                                                          None,
                                                          klass._DBUS_ID,
                                                          klass._DBUS_PATH,
                                                          klass._DBUS_ID,
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

    def set(self, key, variant):
        variant = convert_variant_arg(variant)
        self._get_gss_proxy().Set('(sv)', key, variant)

    def set_async(self, key, variant):
        variant = convert_variant_arg(variant)

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
        return Gio.DBusError.get_remote_error(error) ==\
            'com.hack_computer.GameStateService.KeyError'


class OldGameStateService(GameStateService):
    _proxy = None
    _DBUS_PATH = '/com/endlessm/GameStateService'
    _DBUS_ID = 'com.endlessm.GameStateService'

    def migrate(self):
        self.unlock_lockscreens()
        self.complete_toy_apps_levels()

    def unlock_lockscreens(self):
        keys = [
            'lock.fizzics.1',
            'lock.fizzics.2',
            'lock.OperatingSystemApp.1',
            'lock.OperatingSystemApp.2',
            'lock.OperatingSystemApp.3',
            'lock.lightspeed.1',
            'lock.sidetrack.1',
            'lock.sidetrack.2',
            'lock.sidetrack.3',
            'lock.com.endlessm.Hackdex_chapter_one.1',
            'lock.com.endlessm.Hackdex_chapter_two.1',
        ]

        for key in keys:
            self.set_async(key, {'locked': False})

    def complete_toy_apps_levels(self):
        apps_info = {
            'sidetrack': {
                'key': 'com.endlessm.Sidetrack.State',
                'value': {'availableLevels': 50, 'highestAchievedLevel': 50, 'levelParameters': []},
                'dump-value': True
            }
        }

        for _, info in apps_info.items():
            key, value = info['key'], info['value']
            if info.get('dump-value'):
                value = json.dumps(value)
            self.set_async(key, value)


class ToolBoxTopic(GObject.GObject):

    _INTERFACE_NAME = 'com.hack_computer.HackToolbox.Topic'
    _PATH_TEMPLATE = '/com/hack_computer/HackToolbox/window/{}/topic/{}'
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
                                                         'com.hack_computer.HackToolbox',
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
                'com.hack_computer.HackToolbox',
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


class ToolBoxCodeView(GObject.GObject):

    _INTERFACE_NAME = 'com.hack_computer.HackToolbox.CodeView'
    _PATH_TEMPLATE = '/com/hack_computer/HackToolbox/window/{}/codeview/{}'
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
                                                         'com.hack_computer.HackToolbox',
                                                         self._dbus_path,
                                                         self._INTERFACE_NAME,
                                                         None)

        return self._proxy

    def __init__(self, app_name, topic_name):
        super().__init__()
        self._dbus_path = self._build_dbus_path(app_name, topic_name)
        self._errors_change_handler = self._connect_errors_change()

    def __del__(self):
        self._get_proxy().disconnect(self._errors_change_handler)

    @GObject.Property(type=bool, default=False)
    def errors(self):
        try:
            prop = self._get_proxy().get_cached_property('errors')
            if prop is not None:
                return prop.unpack()
        except GLib.Error as e:
            logger.error(e)
        return False

    def _connect_errors_change(self):
        def _props_changed_cb(_proxy, _changed_properties, _invalidated, *args):
            self.notify('errors')

        return self._get_proxy().connect('g-properties-changed', _props_changed_cb)


class UserAccount(GObject.GObject):

    _INTERFACE_NAME = 'org.freedesktop.Accounts'

    __gsignals__ = {
        'changed': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
    }

    _proxy = None
    _props = None

    @classmethod
    def _ensure_proxy(klass):
        if klass._proxy is None:
            system_bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
            accounts = Gio.DBusProxy.new_sync(system_bus, 0, None,
                                              klass._INTERFACE_NAME,
                                              '/org/freedesktop/Accounts',
                                              klass._INTERFACE_NAME,
                                              None)

            user_path = accounts.FindUserByName('(s)', GLib.get_user_name())

            klass._proxy = Gio.DBusProxy.new_sync(system_bus, 0, None,
                                                  klass._INTERFACE_NAME, user_path,
                                                  'org.freedesktop.Accounts.User',
                                                  None)
            klass._props = Gio.DBusProxy.new_sync(system_bus, 0, None,
                                                  klass._INTERFACE_NAME, user_path,
                                                  'org.freedesktop.DBus.Properties',
                                                  None)

    def __init__(self):
        super().__init__()
        self._ensure_proxy()
        self._proxy.connect('g-signal', self._g_signal_cb)

    def _g_signal_cb(self, proxy, sender_name, signal_name, params):
        if signal_name == 'Changed':
            self.emit('changed')

    def get(self, key):
        return self._props.Get('(ss)', 'org.freedesktop.Accounts.User', key)

    def set_real_name(self, name):
        self._proxy.SetRealName(name)


# Allow to import the HackSoundServer from the system while using a more friendly name
Sound = HackSoundServer
SoundItem = HackSoundItem
