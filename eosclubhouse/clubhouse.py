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
import uuid

from gi.repository import Gdk, Gio, GLib, Gtk, GObject
from eosclubhouse import config, logger, libquest, utils

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
        self._main_image = None
        self.load()

    def _get_id(self):
        return self._id

    def _get_name(self):
        return self._name

    def get_main_image(self):
        return self._main_image

    def get_mood_image(self):
        return self._moods.get(self.mood)

    def get_icon(self):
        image_file = Gio.File.new_for_path(self.get_mood_image())
        icon_bytes = image_file.load_bytes(None)
        return Gio.BytesIcon.new(icon_bytes[0])

    def load(self):
        char_dir = os.path.join(config.CHARACTERS_DIR, self._id)
        self._moods = {}
        for image in os.listdir(char_dir):
            name, ext = os.path.splitext(image)
            path = os.path.join(char_dir, image)
            if name == 'main' or name == self._id:
                self._main_image = path
            else:
                self._moods[name] = path

        # @todo: Raise exception here instead
        assert(self._moods)

        if 'normal' in self._moods.keys():
            self.mood = 'normal'
        else:
            self.mood = list(self._moods.keys())[0]

        # @todo: This fallback should be deleted soon when we have all WIP
        # quests in the right format
        if self._main_image is None:
            self._main_image = self._moods[self.mood]

    id = property(_get_id)
    name = property(_get_name)
    mood = GObject.Property(type=str)


class Message(Gtk.Bin):

    MESSAGE_WIDTH = 300

    def __init__(self):
        super().__init__()
        self._character = None
        self._character_mood_change_handler = 0
        self._setup_ui()

    def _setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/message.ui')

        self.add(builder.get_object('character_talk_box'))
        self.set_size_request(self.MESSAGE_WIDTH, -1)

        self._label = builder.get_object('message_label')
        self._button_box = builder.get_object('message_button_box')
        self._character_image = builder.get_object('character_image')
        self.close_button = builder.get_object('character_message_close_button')
        self.pop_out_button = builder.get_object('character_message_pop_out_button')

    def set_text(self, txt):
        self._label.set_label(txt)

    def get_text(self):
        return self._label.get_label()

    def add_button(self, label, click_cb, *user_data):
        button = Gtk.Button(label=label)
        button.connect('clicked', self._button_clicked_cb, click_cb, *user_data)
        button.show()

        self._button_box.pack_start(button, False, False, 0)
        self._button_box.show()

    def _button_clicked_cb(self, button, caller_cb, *user_data):
        caller_cb(*user_data)
        self.clear_buttons()

    def reset(self):
        self._label.set_label('')
        self.set_character(None)
        self.clear_buttons()

    def clear_buttons(self):
        for child in self._button_box:
            child.destroy()
        self._button_box.hide()

    def set_character(self, character_id):
        if self._character:
            if self._character.id == character_id:
                return

            self._character.disconnect(self._character_mood_change_handler)
            self._character_mood_change_handler = 0
            self._character = None

        if character_id is None:
            return

        self._character = Character(character_id)
        self._character_mood_change_handler = \
            self._character.connect('notify::mood', self._character_mood_changed_cb)
        self._character_mood_changed_cb(self._character)

    def get_character(self):
        return self._character

    def set_character_mood(self, mood):
        if not self._character or mood is None:
            return

        self._character.mood = mood

    def _character_mood_changed_cb(self, character, prop=None):
        image_path = character.get_mood_image()
        logger.debug('Character mood changed: mood=%s image=%s',
                     character.mood, image_path)
        self._character_image.set_from_file(image_path)


class QuestSetButton(Gtk.Button):

    def __init__(self, quest_set):
        super().__init__(halign=Gtk.Align.START,
                         relief=Gtk.ReliefStyle.NONE)

        self.get_style_context().add_class('quest-set-button')

        self._quest_set = quest_set
        character = Character(self._quest_set.get_character())

        # Set the "highlighted" style on "nudge"
        self._quest_set.connect('nudge', lambda _quest_set: self.set_highlighted(True))
        # Reset the "highlighted" style
        self.connect('clicked', lambda _button: self.set_highlighted(False))

        # The button should only be visible when the QuestSet is visible
        self._quest_set.bind_property('visible', self, 'visible',
                                      GObject.BindingFlags.BIDIRECTIONAL |
                                      GObject.BindingFlags.SYNC_CREATE)

        self._image = Gtk.Image.new_from_file(character.get_main_image())
        self._image.show()
        self.add(self._image)

    def get_quest_set(self):
        return self._quest_set

    def get_position(self):
        return self._quest_set.get_position()

    def set_highlighted(self, highlighted):
        highlighted_style = 'highlighted'
        style_context = self.get_style_context()
        if highlighted:
            style_context.add_class(highlighted_style)
        else:
            style_context.remove_class(highlighted_style)


class ClubhousePage(Gtk.EventBox):

    QUEST_NOTIFICATION_ID = 'quest-message'

    def __init__(self, app_window):
        super().__init__(visible=True)

        self._quest_task = None

        self._app_window = app_window
        self._app_window.connect('key-press-event', self._key_press_event_cb)

        self._setup_ui()
        self.get_style_context().add_class('clubhouse-page')
        self._reset_quest_actions()

        self._app_window.connect('show', lambda _window: self._shell_close_popup_message())

    def _setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/clubhouse-page.ui')
        self._message = Message()
        self._overlay_msg_box = builder.get_object('clubhouse_overlay_msg_box')
        self._main_characters_box = builder.get_object('clubhouse_main_characters_box')
        self._clubhouse_message_layer = builder.get_object('clubhouse_message_layer')
        self._clubhouse_message_layer.put(self._message, 0, 0)

        self.add(builder.get_object('clubhouse_overlay'))

        self._message.close_button.connect('clicked', self._quest_close_button_clicked_cb)
        self._message.pop_out_button.connect('clicked', self._quest_pop_out_button_clicked_cb)

    def _quest_close_button_clicked_cb(self, button):
        self.stop_quest()

    def _quest_pop_out_button_clicked_cb(self, button):
        self._app_window.hide()
        self._shell_popup_message(self._message.get_text(), self._message.get_character())

    def stop_quest(self):
        # The quest may have been stopped from the Shell quest view, so show the main window
        self._app_window.show()

        if self._quest_task is None:
            return

        cancellable = self._quest_task.get_cancellable()
        if not cancellable.is_cancelled():
            logger.debug('Stopping quest %s', self._quest_task.get_source_object())
            cancellable.cancel()

        self._message.hide()
        self._overlay_msg_box.hide()
        self._message.close_button.hide()
        self._message.pop_out_button.hide()
        self._quest_task = None

    def add_quest_set(self, quest_set):
        button = QuestSetButton(quest_set)
        button.connect('clicked', self._button_clicked_cb)

        x, y = button.get_position()
        self._main_characters_box.put(button, x, y)

    def _button_clicked_cb(self, button):
        quest_set = button.get_quest_set()
        new_quest = quest_set.get_next_quest()

        self._message.reset()

        character = new_quest.get_main_character() if new_quest else quest_set.get_character()
        self._message.set_character(character)

        if new_quest is None:
            msg_text = quest_set.get_empty_message()
            # If a QuestSet has overridden the empty message to be None, then don't
            # show anything
            if msg_text is None:
                return

            self.show_question(msg_text, [('Ok', self._replied_to_message, None)])
        else:
            self.show_question(new_quest.get_initial_message(),
                               [('Sure!', self._replied_to_message, new_quest),
                                ('Not now…', self._replied_to_message, None)])

        # @todo: Implement the custom allocation for the message  and pass the allocation to
        # it on construction

        self._message.close_button.hide()
        self._message.pop_out_button.hide()
        self._overlay_msg_box.show_all()

        allocation = button.get_allocation()
        self._clubhouse_message_layer.move(self._message,
                                           self.get_allocated_width() * .1, allocation.y)
        self._clubhouse_message_layer.show_all()

    def _replied_to_message(self, quest_to_start):
        self._message.hide()
        if quest_to_start is not None:
            logger.info('Start quest {}'.format(quest_to_start))
            self.run_quest(quest_to_start)
        else:
            self._overlay_msg_box.hide()

    def connect_quest(self, quest):
        quest.connect('message', self._quest_message_cb)
        quest.connect('question', self._quest_question_cb)

    def disconnect_quest(self, quest):
        quest.disconnect_by_func(self._quest_message_cb)
        quest.disconnect_by_func(self._quest_question_cb)

    def run_quest(self, quest):
        self._message.reset()
        self._message.set_character(quest.get_main_character())

        logger.info('Running quest "%s"', quest)

        self.connect_quest(quest)

        cancellable = Gio.Cancellable()
        self._quest_task = Gio.Task.new(quest, cancellable, self.on_quest_finished)
        quest.set_cancellable(cancellable)

        # Show the close button so the user is able to dismiss the quest
        self._message.close_button.show()
        self._message.pop_out_button.show()

        threading.Thread(target=self._run_task_in_thread, args=(self._quest_task,),
                         name='quest-thread').start()

    def _quest_message_cb(self, quest, message_txt, character_id, character_mood):
        logger.debug('Message: %s character_id=%s mood=%s', message_txt, character_id,
                     character_mood)

        self._reset_quest_actions()

        self._message.set_character(character_id)
        self._message.set_character_mood(character_mood)
        self.show_message(message_txt)

        self._overlay_msg_box.show_all()
        self._shell_popup_message(message_txt, self._message.get_character())

    def _quest_question_cb(self, quest, message_txt, answer_choices, character_id, character_mood):
        logger.debug('Quest: %s mood=%s', message_txt, character_mood)

        self._reset_quest_actions()

        self._message.set_character(character_id)
        self._message.set_character_mood(character_mood)
        self.show_question(message_txt, answer_choices)

        self._overlay_msg_box.show_all()
        self._shell_popup_message(message_txt, self._message.get_character())

    def _run_task_in_thread(self, task):
        quest = task.get_source_object()
        quest.start()
        task.return_boolean(True)

    def on_quest_finished(self, quest, result):
        logger.debug('Quest {} finished'.format(quest))
        self.disconnect_quest(quest)
        quest.save_conf()
        self._overlay_msg_box.hide()

    def _key_press_event_cb(self, window, event):
        # Allow to fully quit the Clubhouse on Ctrl+Escape
        if event.keyval == Gdk.KEY_Escape and (event.state & Gdk.ModifierType.CONTROL_MASK):
            self._app_window.destroy()
            return True

        if self._quest_task:
            event_copy = event.copy()
            quest = self._quest_task.get_source_object()
            quest.on_key_event(event_copy)

        return False

    def _shell_close_popup_message(self):
        self._app_window.get_application().withdraw_notification(self.QUEST_NOTIFICATION_ID)

    def _shell_popup_message(self, text, character):
        if self._app_window.props.visible:
            return

        notification = Gio.Notification()
        notification.set_body(text)
        notification.set_title('')

        if character:
            notification.set_icon(character.get_icon())

        for key, action in self._actions.items():
            label = action[0]
            button_target = "app.quest-user-answer('{}')".format(key)
            notification.add_button(label, button_target)

        self._app_window.get_application().send_notification(self.QUEST_NOTIFICATION_ID,
                                                             notification)

    def show_message(self, txt):
        self._message.clear_buttons()
        self._message.set_text(txt)
        self._message.close_button.show()
        self._message.pop_out_button.show()

        return self._message

    def _reset_quest_actions(self):
        self._actions = {}

    def _add_quest_action(self, action):
        key = str(uuid.uuid1())
        self._actions[key] = action
        return key

    def show_question(self, txt, answer_choices):
        message = self.show_message(txt)
        for answer in answer_choices:
            action_key = self._add_quest_action(answer)
            message.add_button(answer[0], self.quest_action, action_key)
        return message

    def quest_action(self, action_key):
        action = self._actions.get(action_key)

        if action is None:
            logger.debug('Failed to get action for key %s', action_key)
            logger.debug('Current actions: %s', self._actions)
            return

        # Call the action
        callback, args = action[1], action[2:]
        callback(*args)

        self._reset_quest_actions()


class InventoryPage(Gtk.EventBox):

    def __init__(self, app_window):
        super().__init__(visible=True)

        self._app_window = app_window


class ClubhouseWindow(Gtk.ApplicationWindow):

    DEFAULT_WINDOW_WIDTH = 484

    def __init__(self, app):
        if os.environ.get('CLUBHOUSE_NO_SIDE_COMPONENT'):
            super().__init__(application=app, title='Clubhouse')
        else:
            super().__init__(application=app, title='Clubhouse',
                             type_hint=Gdk.WindowTypeHint.DOCK,
                             role='eos-side-component')

        self.clubhouse_page = ClubhousePage(self)
        self.inventory_page = InventoryPage(self)

        self.set_size_request(self.DEFAULT_WINDOW_WIDTH, -1)
        self._setup_ui()

    def _setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/main-window.ui')

        self._main_window_stack = builder.get_object('main_window_stack')

        self._clubhouse_button = builder.get_object('main_window_button_clubhouse')
        self._inventory_button = builder.get_object('main_window_button_inventory')

        page_switcher_data = {self._clubhouse_button: self.clubhouse_page,
                              self._inventory_button: self.inventory_page}

        for button, page_widget in page_switcher_data.items():
            self._main_window_stack.add(page_widget)
            button.connect('clicked', self._page_switch_button_clicked_cb, page_widget)

        self.add(builder.get_object('main_window_overlay'))

    def _page_switch_button_clicked_cb(self, button, page_widget):
        self._main_window_stack.set_visible_child(page_widget)


class ClubhouseApplication(Gtk.Application):

    def __init__(self):
        super().__init__(application_id=CLUBHOUSE_NAME,
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        self._init_style()

        self._window = None
        self._dbus_connection = None

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

        simple_actions = [('stop-quest', self._stop_quest, None),
                          ('quest-user-answer', self._quest_user_answer, GLib.VariantType.new('s'))]

        for name, callback, variant_type in simple_actions:
            action = Gio.SimpleAction.new(name, variant_type)
            action.connect('activate', callback)
            self.add_action(action)

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
        libquest.Registry.load(utils.get_alternative_quests_dir())
        libquest.Registry.load(os.path.dirname(__file__) + '/quests')

        quest_sets = libquest.Registry.get_quest_sets()

        for quest_set in quest_sets:
            self._window.clubhouse_page.add_quest_set(quest_set)

    def _stop_quest(self, *args):
        self._window.clubhouse_page.stop_quest()

    def _quest_user_answer(self, action, action_id):
        self._window.clubhouse_page.quest_action(action_id.unpack())

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
        geometry.x = workarea.x + workarea.width - width
        geometry.y = workarea.y
        geometry.width = width
        geometry.height = workarea.height

        self._window.move(geometry.x, geometry.y)
        self._window.resize(geometry.width, geometry.height)


if __name__ == '__main__':
    app = ClubhouseApplication()
    app.run(sys.argv)
