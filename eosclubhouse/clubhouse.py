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

import gi
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
import os
import sys
import threading

from gi.repository import Gdk, Gio, GLib, Gtk, GObject
from eosclubhouse import config, logger
from eosclubhouse import libquest

CLUBHOUSE_NAME = 'com.endlessm.Clubhouse'
CLUBHOUSE_PATH = '/com/endlessm/Clubhouse'
CLUBHOUSE_IFACE = CLUBHOUSE_NAME

ClubhouseIface = ('<node>'
                  '<interface name="com.endlessm.Clubhouse">'
                  '<method name="show">'
                  '<arg type="u" direction="in" name="timestamp"/>'
                  '</method>'
                  '<method name="hide">'
                  '<arg type="u" direction="in" name="timestamp"/>'
                  '</method>'
                  '<property name="Visible" type="b" access="read"/>'
                  '</interface>'
                  '</node>')


class Character(GObject.GObject):

    def __init__(self, id_, name=None):
        super().__init__()
        self._id = id_
        self._name = name or id_
        self.load()

    def _get_name(self):
        return self._name

    def get_image_path(self):
        return self._moods.get(self.mood)

    def load(self):
        char_dir = os.path.join(config.CHARACTERS_DIR, self._id)
        self._moods = {}
        for image in os.listdir(char_dir):
            name, ext = os.path.splitext(image)
            path = os.path.join(char_dir, image)
            self._moods[name] = path

        # @todo: Raise exception here instead
        assert(self._moods)

        if 'normal' in self._moods.keys():
            self.mood = 'normal'
        else:
            self.mood = self._moods.keys()[0]

    name = property(_get_name)
    mood = GObject.Property(type=str)


class Message(Gtk.Bin):

    def __init__(self):
        super().__init__()
        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/message.ui')
        self.add(builder.get_object('message_box'))
        self._label = builder.get_object('message_label')
        self._button_box = builder.get_object('message_button_box')
        self.show_all()

    def set_text(self, txt):
        self._label.set_label(txt)

    def add_button(self, label, click_cb, *user_data):
        button = Gtk.Button(label=label)
        button.connect('clicked', self._button_clicked_cb, click_cb, *user_data)
        button.show()

        self._button_box.pack_start(button, False, False, 0)
        self._button_box.show()

    def _button_clicked_cb(self, button, caller_cb, *user_data):
        caller_cb(*user_data)
        for child in self._button_box.get_children():
            child.destroy()
        self._button_box.hide()


class QuestWindow(Gtk.Window):

    def __init__(self, app):
        if os.environ.get('CLUBHOUSE_NO_SIDE_COMPONENT'):
            super().__init__(application=app)
        else:
            super().__init__(application=app,
                             type=Gtk.WindowType.POPUP)

        self._key_event_handler = 0
        self._character = None

        self._setup_ui()

    def _setup_ui(self):
        self.get_style_context().add_class('quest-window')
        self.set_size_request(300, -1)

        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/quest-window.ui')
        self._message_box = builder.get_object('character_message_box')
        self._character_image = builder.get_object('character_image')
        self._main_box = builder.get_object('quest_main_box')
        self.add(self._main_box)

        display = Gdk.Display.get_default()
        display.connect('monitor-added', lambda _display, _monitor: self._update_geometry())
        self._update_geometry()

    def _update_geometry(self):
        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor()
        monitor_geometry = monitor.get_geometry()
        allocation = self.get_allocation()

        self.move(monitor_geometry.width - 400,
                  allocation.height / 2 + monitor_geometry.height / 2)

    def connect_quest(self, quest):
        quest.connect('message', self._quest_message_cb)
        quest.connect('question', self._quest_question_cb)
        quest.connect('key-events-request', self._request_key_events_cb)

    def disconnect_quest(self, quest):
        quest.handlers_disconnect_by_func(self._quest_message_cb)
        quest.handlers_disconnect_by_func(self._quest_question_cb)
        quest.handlers_disconnect_by_func(self._request_key_events_cb)

    def run_quest(self, quest):
        self._quest = quest
        self.set_character(self._quest.get_main_character())
        self.show()

        logger.info('Running quest "%s"', quest)

        self.connect_quest(self._quest)

        cancellable = Gio.Cancellable()
        task = Gio.Task.new(self._quest, cancellable, self.on_quest_finished)
        task.set_return_on_cancel(True)

        threading.Thread(target=self._run_task_in_thread, args=(task,), name='quest-thread').start()

    def _quest_message_cb(self, quest, message_txt, character_mood):
        logger.debug('Message: %s mood=%s', character_mood, message_txt)
        self.set_character_mood(character_mood)
        self.show_message(message_txt)

    def _quest_question_cb(self, quest, message_txt, answer_choices, character_mood):
        logger.debug('Quest: %s mood=%s', character_mood, message_txt)
        self.set_character_mood(character_mood)
        self.show_question(message_txt, answer_choices)

    def _run_task_in_thread(self, task):
        quest = task.get_source_object()
        quest.start()
        task.return_boolean(True)

    def on_quest_finished(self, quest, result):
        logger.debug('Quest {} finished'.format(quest))
        self.disconnect_quest(quest)

    def _key_press_event_cb(self, window, event, quest):
        event_copy = event.copy()
        quest.on_key_event(event_copy)

    def _request_key_events_cb(self, quest, events_requested):
        if not ((self._key_event_handler > 0) ^ events_requested):
            return

        if self._key_event_handler == 0:
            self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
            self._key_event_handler = self.connect('key-press-event',
                                                   self._key_press_event_cb, quest)
        else:
            self.handler_disconnect(self._key_event_handler)
            self._key_event_handler = 0

    def show_message(self, txt):
        message = Message()
        message.set_text(txt)
        # @todo: Use a Bin or some other widget now that we don't need to
        # show several messages (which would allow us not to clear the container)
        for child in self._message_box:
            child.destroy()
        self._message_box.pack_start(message, False, False, 0)
        return message

    def show_question(self, txt, answer_choices):
        message = self.show_message(txt)
        for answer in answer_choices:
            text, callback = answer
            message.add_button(text, callback)
        return message

    def set_character(self, character_id):
        self._character = Character(character_id)
        self._character.connect('notify::mood', self._character_mood_changed_cb)
        self._character_mood_changed_cb(self._character)

    def _character_mood_changed_cb(self, character, prop=None):
        logger.debug('Character mood changed: mood=%s image=%s',
                     character.mood, character.get_image_path())
        self._character_image.set_from_file(character.get_image_path())

    def set_character_mood(self, mood):
        if mood is None:
            return
        self._character.mood = mood


class QuestSetButton(Gtk.Button):

    def __init__(self, quest_set):
        super().__init__(halign=Gtk.Align.START,
                         relief=Gtk.ReliefStyle.NONE)

        self.get_style_context().add_class('quest-set-button')

        self._quest_set = quest_set
        character = Character(self._quest_set.get_character())

        self._image = Gtk.Image.new_from_file(character.get_image_path())
        self._image.show()
        self.add(self._image)

    def get_quest_set(self):
        return self._quest_set


class ClubhouseWindow(Gtk.ApplicationWindow):

    DEFAULT_WINDOW_WIDTH = 500

    def __init__(self, app):
        if os.environ.get('CLUBHOUSE_NO_SIDE_COMPONENT'):
            super().__init__(application=app, title='Clubhouse')
        else:
            super().__init__(application=app, title='Clubhouse',
                             type_hint=Gdk.WindowTypeHint.DOCK,
                             role='eos-side-component')

        self.set_size_request(self.DEFAULT_WINDOW_WIDTH, -1)
        self._setup_ui()
        self.get_style_context().add_class('main-window')
        self._character = None

    def _setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/main-window.ui')
        self._main_box = builder.get_object('main_box')
        self._overlay_msg_box = builder.get_object('main_window_overlay_msg_box')
        self._main_window_overlay = builder.get_object('main_window_overlay')
        self.add(self._main_window_overlay)

    def add_quest_set(self, quest_set):
        button = QuestSetButton(quest_set)
        button.connect('clicked', self._button_clicked_cb)

        button.show()
        self._main_box.pack_start(button, False, False, 0)

    def _button_clicked_cb(self, button):
        quest_set = button.get_quest_set()
        new_quest = quest_set().get_next_quest()()

        self._hide_message()

        message = Message()
        message.set_text(new_quest.get_initial_message())

        # @todo: Implement the custom allocation for the message  and pass the allocation to
        # it on construction
        allocation = button.get_allocation()
        message.props.margin_left = allocation.x + allocation.width - allocation.width * .25
        message.props.margin_top = allocation.y

        message.add_button('Sure!', self._replied_to_message, new_quest)
        message.add_button('Not now…', self._replied_to_message, None)

        self._overlay_msg_box.add(message)
        self._overlay_msg_box.show()

    def _replied_to_message(self, quest_to_start):
        if quest_to_start is not None:
            logger.info('Start quest {}'.format(quest_to_start))
            self._quest_window = QuestWindow(self.get_application())
            self._quest_window.run_quest(quest_to_start)
            self.hide()

        self._hide_message()

    def _hide_message(self):
        message = self._overlay_msg_box.get_child()
        if message is not None:
            message.destroy()


class ClubhouseApplication(Gtk.Application):

    def __init__(self):
        super().__init__(application_id=CLUBHOUSE_NAME,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self._init_style()

        self._window = None
        self._dbus_connection = None

        self._key_event_handler = 0

    def _init_style(self):
        self.props.resource_base_path = '/com/endlessm/Clubhouse'
        # @todo: Move the resource to a different dir
        resource = Gio.resource_load(os.path.join(os.path.dirname(__file__),
                                                  'eos-clubhouse.gresource'))
        Gio.Resource._register(resource)
        css_file = Gio.File.new_for_uri('resource:///com/endlessm/Clubhouse/gtk-style.css')
        css_provider = Gtk.CssProvider()
        css_provider.load_from_file(css_file)
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(Gdk.Screen.get_default(),
                                              css_provider,
                                              Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def do_activate(self):
        pass

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self._window = ClubhouseWindow(self)
        self._window.connect('notify::visible', self._vibility_notify_cb)

        display = Gdk.Display.get_default()
        display.connect('monitor-added',
                        lambda disp, monitor: self._update_geometry())

        monitor = display.get_primary_monitor()
        if monitor:
            monitor.connect('notify::workarea',
                            lambda klass, args: self._update_geometry())

        self._update_geometry()
        self._window.show()

        # @todo: Use a location from config
        libquest.Registry.load(os.path.dirname(__file__) + '/quests')
        quest_sets = libquest.Registry.get_quest_sets()

        for quest_set in quest_sets:
            self._window.add_quest_set(quest_set)

    def _vibility_notify_cb(self, window, pspec):
        changed_props = {'Visible': GLib.Variant('b', self._window.is_visible())}
        variant = GLib.Variant.new_tuple(GLib.Variant('s', CLUBHOUSE_IFACE),
                                         GLib.Variant('a{sv}', changed_props),
                                         GLib.Variant('as', []))
        self._dbus_connection.emit_signal(None,
                                          CLUBHOUSE_PATH,
                                          'org.freedesktop.DBus.Properties',
                                          'PropertiesChanged',
                                          variant)

    def do_dbus_register(self, connection, path):
        self._dbus_connection = connection

        introspection_data = Gio.DBusNodeInfo.new_for_xml(ClubhouseIface)
        connection.register_object(path,
                                   introspection_data.interfaces[0],
                                   self.handle_method_call,
                                   self.handle_get_property)
        return Gtk.Application.do_dbus_register(self, connection, path)

    def handle_method_call(self, connection, sender, object_path, interface_name,
                           method_name, parameters, invocation):
        args = parameters.unpack()
        if not hasattr(self, method_name):
            invocation.return_dbus_error("org.gtk.GDBus.Failed",
                                         "This method is not implemented")
            return

        getattr(self, method_name)(*args)

    def handle_get_property(self, connection, sender, object_path,
                            interface, key):
        if key == 'Visible':
            return GLib.Variant('b', self._window.is_visible())

        return None

    def show(self, timestamp):
        self._window.show()
        self._window.present_with_time(int(timestamp))

    def hide(self, timestamp):
        self._window.hide()

    def _update_geometry(self):
        monitor = Gdk.Display.get_default().get_primary_monitor()
        if not monitor:
            return
        workarea = monitor.get_workarea()
        width = self._window.get_size()[0]

        geometry = Gdk.Rectangle()
        geometry.x = workarea.width - width
        geometry.y = workarea.y
        geometry.width = width
        geometry.height = workarea.height

        self._window.move(geometry.x, geometry.y)
        self._window.resize(geometry.width, geometry.height)


if __name__ == '__main__':
    app = ClubhouseApplication()
    app.run(sys.argv)
