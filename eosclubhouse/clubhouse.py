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
gi.require_version('Json', '1.0')
import os
import sys
import threading

from gi.repository import Gdk, Gio, GLib, Gtk, GObject, Json
from eosclubhouse import logger, libquest, utils
from eosclubhouse.system import GameStateService, Sound
from eosclubhouse.utils import Performance
from eosclubhouse.animation import Animation, AnimationImage, AnimationSystem, Animator, \
    get_character_animation_dirs


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
                  '<method name="getAnimationMetadata">'
                  '<arg type="s" direction="in" name="uri"/>'
                  '<arg type="v" direction="out" name="metadata"/>'
                  '</method>'
                  '<property name="Visible" type="b" access="read"/>'
                  '<property name="SuggestingOpen" type="b" access="read"/>'
                  '</interface>'
                  '</node>')

DEFAULT_WINDOW_WIDTH = 484


class Character(GObject.GObject):
    _characters = {}
    DEFAULT_MOOD = 'talk'

    @classmethod
    def get_or_create(class_, character_id):
        if character_id not in class_._characters:
            character = class_(character_id)
            class_._characters[character_id] = character
        return class_._characters[character_id]

    def __init__(self, id_):
        super().__init__()
        self._id = id_
        self._mood = self.DEFAULT_MOOD
        self._fullbody_image = None
        self.load()

    def _get_id(self):
        return self._id

    def _get_mood(self):
        return self._mood

    def _set_mood(self, mood):
        if mood is None:
            mood = self.DEFAULT_MOOD
        self._mood = mood

    def get_fullbody_image(self):
        return self._fullbody_image

    def get_moods_path(self):
        return os.path.join(self._id, 'moods')

    def get_mood_icon(self):
        mood_path = self.get_moods_path()

        mood_image = None
        for sprites_path in get_character_animation_dirs(mood_path):
            test_image = os.path.join(sprites_path, self._mood + '.png')
            if not os.path.exists(test_image):
                continue
            mood_image = test_image

        image_file = Gio.File.new_for_path(mood_image)
        return Gio.FileIcon.new(image_file)

    def load(self):
        fullbody_path = os.path.join(self._id, 'fullbody')
        self._fullbody_image = AnimationImage(fullbody_path)
        self._fullbody_image.play('idle')

    id = property(_get_id)
    mood = GObject.Property(_get_mood, _set_mood, type=str)


class Message(Gtk.Bin):

    __gsignals__ = {
        'closed': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
    }

    _MARGIN = 20
    _LABEL_MARGIN = 30

    CHARACTER_HEIGHT = 155
    BUTTON_HEIGHT = 35
    LABEL_WIDTH = DEFAULT_WINDOW_WIDTH - _MARGIN * 2 - _LABEL_MARGIN
    MESSAGE_HEIGHT = CHARACTER_HEIGHT + _MARGIN * 2 + BUTTON_HEIGHT / 2

    def __init__(self):
        super().__init__()
        self._character = None
        self._character_mood_change_handler = 0
        self._setup_ui()
        self._animator = Animator(self._character_image)
        self.connect("show", lambda _: Sound.play('clubhouse/dialog/open'))

    def _setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/message.ui')

        overlay = builder.get_object('character_talk_box')
        self.add(overlay)

        self.set_size_request(-1, self.MESSAGE_HEIGHT)

        self._label = builder.get_object('message_label')
        self._label.set_size_request(self.LABEL_WIDTH, -1)

        self.close_button = builder.get_object('character_message_close_button')
        self.close_button.connect('clicked', self._close_button_clicked_cb)

        self._character_image = builder.get_object('character_image')
        overlay.set_overlay_pass_through(self._character_image, True)

        self._button_box = builder.get_object('message_button_box')

    def _close_button_clicked_cb(self, button):
        self.close()

    def set_text(self, txt):
        self._label.set_label(txt)

    def get_text(self):
        return self._label.get_label()

    def add_button(self, label, click_cb, *user_data):
        button = Gtk.Button(label=label)

        if len(self._button_box.get_children()) == 0:
            image = Gtk.Image.new_from_resource(
                '/com/endlessm/Clubhouse/images/icon_check-in-circle.svg')
            button.set_image(image)
            button.set_property('always-show-image', True)

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

    def close(self):
        if not self.is_visible():
            return

        self.hide()
        Sound.play('clubhouse/dialog/close')
        self.emit('closed')

    def set_character(self, character_id):
        if self._character:
            if self._character.id == character_id:
                return

            self._character.disconnect(self._character_mood_change_handler)
            self._character_mood_change_handler = 0
            self._character = None

        if character_id is None:
            return

        self._character = Character.get_or_create(character_id)
        self._character_mood_change_handler = \
            self._character.connect('notify::mood', self._character_mood_changed_cb)
        self._character_mood_changed_cb(self._character)

    def get_character(self):
        return self._character

    def _character_mood_changed_cb(self, character, prop=None):
        logger.debug('Character mood changed: mood=%s',
                     character.mood)

        animation_id = '{}/{}'.format(character.id, character.mood)
        if not self._animator.has_animation(animation_id):
            self._animator.load(character.get_moods_path(), character.id)

        self._animator.play(animation_id)


class QuestSetButton(Gtk.Button):

    def __init__(self, quest_set):
        super().__init__(halign=Gtk.Align.START,
                         relief=Gtk.ReliefStyle.NONE)

        self.get_style_context().add_class('quest-set-button')

        self._quest_set = quest_set
        character = Character.get_or_create(self._quest_set.get_character())

        self._image = character.get_fullbody_image()
        self._image.show()
        self.add(self._image)

        self._set_highlighted(self._quest_set.highlighted)

        self._quest_set.connect('notify::highlighted', self._on_quest_set_highlighted_changed)

        # The button should only be visible when the QuestSet is visible
        self._quest_set.bind_property('visible', self, 'visible',
                                      GObject.BindingFlags.BIDIRECTIONAL |
                                      GObject.BindingFlags.SYNC_CREATE)

    def get_quest_set(self):
        return self._quest_set

    def get_position(self):
        return self._quest_set.get_position()

    def _on_quest_set_highlighted_changed(self, _quest_set, _param):
        self._set_highlighted(self._quest_set.highlighted)

    def _set_highlighted(self, highlighted):
        highlighted_style = 'highlighted'
        style_context = self.get_style_context()
        if highlighted:
            self._image.play('hi')
            style_context.add_class(highlighted_style)
        else:
            self._image.play('idle')
            style_context.remove_class(highlighted_style)


class ClubhousePage(Gtk.EventBox):

    def __init__(self, app_window):
        super().__init__(visible=True)

        self._quest_task = None

        self._app_window = app_window
        self._app_window.connect('key-press-event', self._key_press_event_cb)

        self._setup_ui()
        self.get_style_context().add_class('clubhouse-page')
        self._reset_quest_actions()

        self._current_quest_notification = None

        self.add_tick_callback(AnimationSystem.step)

    def _setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/clubhouse-page.ui')
        self._message = Message()
        self._message.connect('closed', self._hide_message_overlay_cb)
        self._overlay_msg_box = builder.get_object('clubhouse_overlay_msg_box')
        self._main_characters_box = builder.get_object('clubhouse_main_characters_box')
        self._overlay_msg_box.add(self._message)

        self.add(builder.get_object('clubhouse_overlay'))

        self._main_box = builder.get_object('clubhouse_main_box')
        self._main_box.connect('button-press-event', self._on_button_press_event_cb)

    def _hide_message_overlay_cb(self, message):
        self._overlay_msg_box.hide()

    def _on_button_press_event_cb(self, main_box, event):
        if event.get_button().button == 1:
            self._message.close()
            return True

        return False

    def stop_quest(self):
        self._cancel_ongoing_task()

    def quest_debug_skip(self):
        if self._quest_task is not None:
            quest = self._quest_task.get_source_object()
            quest.set_debug_skip(True)

    def _cancel_ongoing_task(self):
        if self._quest_task is None:
            return

        cancellable = self._quest_task.get_cancellable()
        if not cancellable.is_cancelled():
            logger.debug('Stopping quest %s', self._quest_task.get_source_object())
            cancellable.cancel()

        self._quest_task = None

    def add_quest_set(self, quest_set):
        button = QuestSetButton(quest_set)
        quest_set.connect('notify::highlighted', self._on_quest_set_highlighted_changed)
        button.connect('clicked', self._button_clicked_cb)

        x, y = button.get_position()
        self._main_characters_box.put(button, x, y)

    def _on_quest_set_highlighted_changed(self, quest_set, _param):
        if self._app_window.is_visible():
            return

        self._app_window.get_application().send_suggest_open(
            libquest.Registry.has_quest_sets_highlighted())

    def _button_clicked_cb(self, button):
        quest_set = button.get_quest_set()
        new_quest = quest_set.get_next_quest()
        self._message.reset()

        # If a quest from this quest_set is already running, then just hide the window so the
        # user focuses on the Shell's quest dialog
        if self._quest_task:
            quest = self._quest_task.get_source_object()
            if quest in quest_set.get_quests():
                self._shell_show_current_popup_message()
                quest.set_to_foreground()
                self._app_window.hide()
                # Hide the message here because it may be showing from another quest set
                self._overlay_msg_box.hide()
                return

        character = new_quest.get_main_character() if new_quest else quest_set.get_character()
        self._message.set_character(character)

        if new_quest is None:
            msg_text = quest_set.get_empty_message()
            # If a QuestSet has overridden the empty message to be None, then don't
            # show anything
            if msg_text is None:
                return

            self.show_message(msg_text, [('Ok', self._message.close)])
        else:
            self.show_message(new_quest.get_initial_message(),
                              [('Sure!', self._accept_quest_message, quest_set, new_quest),
                               ('Not now…', self._message.close)])

        self._overlay_msg_box.show_all()

    def _accept_quest_message(self, quest_set, new_quest):
        self._message.hide()
        self._overlay_msg_box.hide()
        logger.info('Start quest {}'.format(new_quest))
        quest_set.set_property('highlighted', False)
        self.run_quest(new_quest)

    def connect_quest(self, quest):
        quest.connect('message', self._quest_message_cb)
        quest.connect('item-given', self._quest_item_given_cb)

    def disconnect_quest(self, quest):
        quest.disconnect_by_func(self._quest_message_cb)
        quest.disconnect_by_func(self._quest_item_given_cb)

    def run_quest(self, quest):
        logger.info('Running quest "%s"', quest)

        self._cancel_ongoing_task()

        self.connect_quest(quest)

        cancellable = Gio.Cancellable()
        self._quest_task = Gio.Task.new(quest, cancellable, self.on_quest_finished)
        quest.set_cancellable(cancellable)

        # Hide the window so the user focuses on the Shell Quest View
        self._app_window.hide()

        threading.Thread(target=self._run_task_in_thread, args=(self._quest_task,),
                         name='quest-thread').start()

    def run_quest_by_name(self, quest_name, use_shell_quest_view):
        quest = libquest.Registry.get_quest_by_name(quest_name)
        if quest is None:
            logger.warning('No quest with name "%s" found!', quest_name)
            return

        if self._is_current_quest(quest):
            logger.warning('Quest "%s" is already being run!', quest_name)
            return

        self._cancel_ongoing_task()

        if use_shell_quest_view:
            self._app_window.hide()
        self.run_quest(quest)

    def _is_current_quest(self, quest):
        return self._quest_task is not None and self._quest_task.get_source_object() == quest

    def _quest_item_given_cb(self, quest, item_id, text):
        self._shell_popup_item(item_id, text)

    def _quest_message_cb(self, quest, message_txt, answer_choices, character_id, character_mood,
                          open_dialog_sound):
        logger.debug('Message: %s character_id=%s mood=%s choices=[%s]', message_txt, character_id,
                     character_mood, '|'.join([answer for answer, _cb in answer_choices]))

        self._reset_quest_actions()

        for answer in answer_choices:
            self._add_quest_action(answer)

        character = Character.get_or_create(character_id)
        character.mood = character_mood

        self._shell_popup_message(message_txt, character, open_dialog_sound)

    def _run_task_in_thread(self, task):
        quest = task.get_source_object()
        quest.start()
        task.return_boolean(True)

    def on_quest_finished(self, quest, result):
        logger.debug('Quest {} finished'.format(quest))
        self.disconnect_quest(quest)
        quest.save_conf()
        quest.dismiss()

        # Ensure we reset the running quest (only if we haven't started a different quest in the
        # meanwhile) quest and close any eventual message popups
        if self._is_current_quest(quest):
            self._quest_task = None

        if self._quest_task is None:
            self._shell_close_popup_message()

        self._current_quest_notification = None

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
        self._app_window.get_application().close_quest_msg_notification()

    def _shell_popup_message(self, text, character, open_dialog_sound):
        notification = Gio.Notification()
        notification.set_body(text)
        notification.set_title('')

        if open_dialog_sound:
            Sound.play(open_dialog_sound)
        if character:
            notification.set_icon(character.get_mood_icon())
            Sound.play('clubhouse/{}/mood/{}'.format(character.id,
                                                     character.mood))

        for key, action in self._actions.items():
            label = action[0]
            button_target = "app.quest-user-answer('{}')".format(key)
            notification.add_button(label, button_target)

        # Add debug button (e.g. to quickly skip steps)
        if self._app_window.get_application().has_debug_mode():
            notification.add_button('🐞', 'app.quest-debug-skip')

        self._app_window.get_application().send_quest_msg_notification(notification)
        self._current_quest_notification = (notification, open_dialog_sound)

    def _shell_show_current_popup_message(self):
        if self._current_quest_notification is None:
            return

        notification, sound = self._current_quest_notification

        if sound:
            Sound.play(sound)

        self._app_window.get_application().send_quest_msg_notification(notification)

    def _shell_popup_item(self, item_id, text):
        item = utils.QuestItemDB.get_item(item_id)
        if item is None:
            logger.debug('Failed to get item %s from DB', item_id)
            return

        icon_name, _icon_used_name, item_name = item

        notification = Gio.Notification()
        if text is None:
            text = 'Got new item!! {}'.format(item_name)

        notification.set_body(text)
        notification.set_title('')

        icon_file = Gio.File.new_for_path(utils.QuestItemDB.get_icon_path(icon_name))
        icon_bytes = icon_file.load_bytes(None)
        icon = Gio.BytesIcon.new(icon_bytes[0])

        notification.set_icon(icon)

        notification.add_button('OK', 'app.item-accept-answer')
        notification.add_button('Show me', "app.show-page('{}')".format('inventory'))

        self._app_window.get_application().send_quest_item_notification(notification)

    def show_message(self, txt, answer_choices=[]):
        self._message.clear_buttons()
        self._message.set_text(txt)

        for answer in answer_choices:
            action_key = self._add_quest_action(answer)
            self._message.add_button(answer[0], self.quest_action, action_key)

        return self._message

    def _reset_quest_actions(self):
        self._actions = {}

    def _add_quest_action(self, action):
        # Lazy import UUID module because it takes a while to do so, and we only need it here
        import uuid

        key = str(uuid.uuid1())
        self._actions[key] = action
        return key

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

    def set_quest_to_background(self):
        if self._quest_task:
            quest = self._quest_task.get_source_object()
            quest.set_to_background()


class InventoryItem(Gtk.Box):

    def __init__(self, item_id, is_used, icon_name, icon_used_name, item_name):
        super().__init__(halign=Gtk.Align.CENTER,
                         orientation=Gtk.Orientation.VERTICAL,
                         visible=True,
                         spacing=16,
                         width_request=150)

        self.item_id = item_id
        self.is_used = is_used
        self._icon_name = icon_name
        self._icon_used_name = icon_used_name

        self.get_style_context().add_class('inventory-item')

        self._image = Gtk.Image(width_request=150, height_request=150, yalign=1.0)
        self.add(self._image)

        self.add(Gtk.Label.new(item_name))
        self._update_icon()
        self.show_all()

    def _update_icon(self):
        icon_name = self._icon_name
        if self.is_used:
            icon_name = self._icon_used_name

        icon_path = utils.QuestItemDB.get_icon_path(icon_name)
        self._image.set_from_file(icon_path)

    def set_used(self, is_used):
        self.is_used = is_used
        self._update_icon()


class InventoryPage(Gtk.EventBox):

    def __init__(self, app_window):
        super().__init__(visible=True)

        self._app_window = app_window

        self._setup_ui()

        self._gss = GameStateService()
        self._gss.connect('changed', lambda _gss: self._load_items())
        self._items_db = utils.QuestItemDB()

        self._loaded_items = {}
        self._update_state()

        self._load_items()

    def _setup_ui(self):
        self.get_style_context().add_class('inventory-page')

        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/inventory-page.ui')

        self._inventory_stack = builder.get_object('inventory_stack')

        self._inventory_empty_state_box = builder.get_object('inventory_empty_state_box')

        self._inventory_box = builder.get_object('inventory_box')
        self._inventory_box.set_sort_func(self._sort_items)

        scrolled_window = builder.get_object('inventory_scrolled_window')
        self.add(scrolled_window)

    def _sort_items(self, child_1, child_2):
        item_1 = child_1.get_children()[0]
        item_2 = child_2.get_children()[0]
        return int(item_1.is_used) - int(item_2.is_used)

    def _add_item(self, item_id, is_used, icon_name, icon_used_name, item_name):
        if item_id in self._loaded_items:
            item = self._loaded_items[item_id]
            item.set_used(is_used)
            return

        new_item = InventoryItem(item_id, is_used, icon_name, icon_used_name, item_name)
        self._loaded_items[item_id] = new_item
        self._inventory_box.add(new_item)

    def _remove_item(self, item_id):
        item = self._loaded_items.get(item_id)
        if item:
            item.destroy()
            del self._loaded_items[item_id]

    def _load_items(self):
        # For now there is no method in the GameStateService to retrieve items based
        # on a prefix, so every time there's a change in the service, we need to directly
        # verify all the items we're interested in.
        for item_id, (icon, icon_used, name) in self._items_db.get_all_items():
            item_state = self._gss.get(item_id)
            if item_state is None:
                self._remove_item(item_id)
                continue

            # Used keys shouldn't show up in the inventory if are consume-able
            if (self._item_is_key(item_id) and
               item_state.get('used', False) and
               item_state.get('consume_after_use', True)):
                self._remove_item(item_id)
                continue

            is_used = item_state.get('used', False)
            self._add_item(item_id, is_used, icon, icon_used, name)

        self._update_state()

    def _update_state(self):
        if len(self._loaded_items) > 0:
            self._inventory_stack.set_visible_child(self._inventory_box)
        else:
            self._inventory_stack.set_visible_child(self._inventory_empty_state_box)

    def _item_is_key(self, item_id):
        return item_id.startswith('item.key.')


class EpisodesPage(Gtk.EventBox):

    def __init__(self, app_window):
        super().__init__(visible=True)

        self._app_window = app_window
        self._setup_ui()

    def _setup_ui(self):
        self.get_style_context().add_class('episodes-page')


class ClubhouseWindow(Gtk.ApplicationWindow):

    _MAIN_PAGE_RESET_TIMEOUT = 60  # sec

    def __init__(self, app):
        if os.environ.get('CLUBHOUSE_NO_SIDE_COMPONENT'):
            super().__init__(application=app, title='Clubhouse')
        else:
            super().__init__(application=app, title='Clubhouse',
                             type_hint=Gdk.WindowTypeHint.NORMAL,
                             role='eos-side-component',
                             skip_taskbar_hint=True,
                             decorated=False)

            self.connect('realize', self._window_realize_cb)

        self.set_keep_above(True)

        self.clubhouse_page = ClubhousePage(self)
        self.inventory_page = InventoryPage(self)
        self.episodes_page = EpisodesPage(self)

        self.set_size_request(DEFAULT_WINDOW_WIDTH, -1)
        self._setup_ui()

        self._page_reset_timeout = 0
        self._ambient_sound_uuid = None
        self.connect('notify::visible', self._on_visibile_property_changed)

        display = Gdk.Display.get_default()
        display.connect('monitor-added',
                        lambda disp, monitor: self._update_geometry())

        monitor = display.get_primary_monitor()
        if monitor:
            monitor.connect('notify::workarea',
                            lambda klass, args: self._update_geometry())

        self._update_geometry()

    def _setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/main-window.ui')

        self._main_window_stack = builder.get_object('main_window_stack')

        self._clubhouse_button = builder.get_object('main_window_button_clubhouse')
        self._inventory_button = builder.get_object('main_window_button_inventory')
        self._episodes_button = builder.get_object('main_window_button_episodes')

        page_switcher_data = {self._clubhouse_button: self.clubhouse_page,
                              self._inventory_button: self.inventory_page,
                              self._episodes_button: self.episodes_page}

        for button, page_widget in page_switcher_data.items():
            self._main_window_stack.add(page_widget)
            button.connect('clicked', self._page_switch_button_clicked_cb, page_widget)

        self.add(builder.get_object('main_window_overlay'))

    def _window_realize_cb(self, window):
        def _window_focus_out_event_cb(_window, _event):
            self.hide()
            return False

        gdk_window = self.get_window()
        gdk_window.set_functions(0)
        gdk_window.set_events(gdk_window.get_events() | Gdk.EventMask.FOCUS_CHANGE_MASK)

        self.connect('focus-out-event', _window_focus_out_event_cb)

    def _page_switch_button_clicked_cb(self, button, page_widget):
        self._main_window_stack.set_visible_child(page_widget)

    def set_page(self, page_name):
        page_buttons = {'clubhouse': self._clubhouse_button,
                        'inventory': self._inventory_button,
                        'episodes': self._episodes_button}

        button = page_buttons.get(page_name)

        if button is not None:
            button.set_active(True)

    def _update_geometry(self):
        monitor = Gdk.Display.get_default().get_primary_monitor()
        if not monitor:
            return

        workarea = monitor.get_workarea()
        width = DEFAULT_WINDOW_WIDTH

        geometry = Gdk.Rectangle()
        geometry.x = workarea.x + workarea.width - width
        geometry.y = workarea.y
        geometry.width = width
        geometry.height = workarea.height

        self.move(geometry.x, geometry.y)
        self.resize(geometry.width, geometry.height)

    def _select_main_page_on_timeout(self):
        self._clubhouse_button.set_active(True)
        self._page_reset_timeout = 0

        return GLib.SOURCE_REMOVE

    def _stop_page_reset_timeout(self):
        if self._page_reset_timeout > 0:
            GLib.source_remove(self._page_reset_timeout)
            self._page_reset_timeout = 0

    def _reset_selected_page_on_timeout(self):
        self._stop_page_reset_timeout()

        if self._clubhouse_button.get_active():
            return

        self._page_reset_timeout = GLib.timeout_add_seconds(self._MAIN_PAGE_RESET_TIMEOUT,
                                                            self._select_main_page_on_timeout)

    def _on_visibile_property_changed(self, _window, _param):
        if self.props.visible:
            self._stop_page_reset_timeout()
            Sound.play('clubhouse/ambient', self._ambient_sound_uuid_cb)
        else:
            self._reset_selected_page_on_timeout()
            self.stop_ambient_sound()

    def _ambient_sound_uuid_cb(self, _proxy, uuid, _data):
        if isinstance(uuid, GLib.Error):
            logger.warning('Error when attempting to play sound: %s', uuid.message)
            self._ambient_sound_uuid = None
            return

        self._ambient_sound_uuid = uuid

    def stop_ambient_sound(self):
        if self._ambient_sound_uuid:
            Sound.stop(self._ambient_sound_uuid)
            self._ambient_sound_uuid = None

    def hide(self):
        super().hide()
        # We update the geometry here to ensure the window will still slide in to the right place
        # the second time it's opened (for some reason, without this it will slide all the way to
        # the left of the screen)
        self._update_geometry()


class ClubhouseApplication(Gtk.Application):

    QUEST_MSG_NOTIFICATION_ID = 'quest-message'
    QUEST_ITEM_NOTIFICATION_ID = 'quest-item'

    def __init__(self):
        super().__init__(application_id=CLUBHOUSE_NAME,
                         resource_base_path='/com/endlessm/Clubhouse')

        self._window = None
        self._debug_mode = False
        self._registry_loaded = False
        self._suggesting_open = False

        # @todo: Move the resource to a different dir
        resource = Gio.resource_load(os.path.join(os.path.dirname(__file__),
                                                  'eos-clubhouse.gresource'))
        Gio.Resource._register(resource)

        self.add_main_option('list-quests', ord('q'), GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'List existing quest sets and quests', None)
        self.add_main_option('debug', ord('d'), GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'Turn on debug mode', None)
        self.add_main_option('quit', ord('x'), GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'Fully close the application', None)

    def _init_style(self):
        css_file = Gio.File.new_for_uri('resource:///com/endlessm/Clubhouse/gtk-style.css')
        css_provider = Gtk.CssProvider()
        css_provider.load_from_file(css_file)
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(Gdk.Screen.get_default(),
                                              css_provider,
                                              Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    @Performance.timeit
    def do_activate(self):
        self.show(Gdk.CURRENT_TIME)

    def do_handle_local_options(self, options):
        if options.contains('list-quests'):
            self._list_quests()
            return 0

        if options.contains('debug'):
            self.register(None)
            self.activate_action('debug-mode', GLib.Variant('b', True))

        if options.contains('quit'):
            self.register(None)
            self.activate_action('quit', None)

        return -1

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self._ensure_registry_loaded()
        self._init_style()

        simple_actions = [('debug-mode', self._debug_mode_action_cb, GLib.VariantType.new('b')),
                          ('item-accept-answer', self._item_accept_action_cb, None),
                          ('quest-debug-skip', self._quest_debug_skip, None),
                          ('quest-user-answer', self._quest_user_answer, GLib.VariantType.new('s')),
                          ('quest-view-close', self._quest_view_close_action_cb, None),
                          ('quit', self._quit_action_cb, None),
                          ('run-quest', self._run_quest_action_cb, GLib.VariantType.new('(sb)')),
                          ('show-page', self._show_page_action_cb, GLib.VariantType.new('s')),
                          ('stop-quest', self._stop_quest, None),
                          ]

        for name, callback, variant_type in simple_actions:
            action = Gio.SimpleAction.new(name, variant_type)
            action.connect('activate', callback)
            self.add_action(action)

    def _ensure_registry_loaded(self):
        if not self._registry_loaded:
            # @todo: Use a location from config
            libquest.Registry.load(utils.get_alternative_quests_dir())
            libquest.Registry.load(os.path.dirname(__file__) + '/quests')
            self._registry_loaded = True

            # Check if we need to set the SuggestingOpen property
            quest_sets = libquest.Registry.get_quest_sets()
            for quest_set in quest_sets:
                if quest_set.highlighted:
                    self.send_suggest_open(True)
                    break

    def _ensure_window(self):
        if self._window:
            return

        self._window = ClubhouseWindow(self)
        self._window.connect('notify::visible', self._vibility_notify_cb)

        quest_sets = libquest.Registry.get_quest_sets()
        for quest_set in quest_sets:
            self._window.clubhouse_page.add_quest_set(quest_set)

    def send_quest_msg_notification(self, notification):
        self.send_notification(self.QUEST_MSG_NOTIFICATION_ID, notification)

    def close_quest_msg_notification(self):
        self.withdraw_notification(self.QUEST_MSG_NOTIFICATION_ID)

    def send_quest_item_notification(self, notification):
        self.send_notification(self.QUEST_ITEM_NOTIFICATION_ID, notification)

    def close_quest_item_notification(self):
        self.withdraw_notification(self.QUEST_ITEM_NOTIFICATION_ID)

    def send_suggest_open(self, suggest):
        if suggest == self._suggesting_open:
            return

        self._suggesting_open = suggest
        changed_props = {'SuggestingOpen': GLib.Variant('b', self._suggesting_open)}
        variant = GLib.Variant.new_tuple(GLib.Variant('s', CLUBHOUSE_IFACE),
                                         GLib.Variant('a{sv}', changed_props),
                                         GLib.Variant('as', []))
        self.get_dbus_connection().emit_signal(None,
                                               CLUBHOUSE_PATH,
                                               'org.freedesktop.DBus.Properties',
                                               'PropertiesChanged',
                                               variant)

    def _stop_quest(self, *args):
        if (self._window):
            self._window.clubhouse_page.stop_quest()
        self.close_quest_msg_notification()

    def _item_accept_action_cb(self, action, arg_variant):
        # This is a no-op
        logger.debug('Item accept button clicked')

    def _debug_mode_action_cb(self, action, arg_variant):
        self._debug_mode = arg_variant.unpack()

    def _quest_user_answer(self, action, action_id):
        if self._window:
            self._window.clubhouse_page.quest_action(action_id.unpack())

    def _quest_view_close_action_cb(self, _action, _action_id):
        logger.debug('Shell quest view closed')
        if self._window:
            self._window.clubhouse_page.set_quest_to_background()

    def _quest_debug_skip(self, action, action_id):
        if self._window:
            self._window.clubhouse_page.quest_debug_skip()

    def _run_quest_action_cb(self, action, arg_variant):
        self._ensure_window()
        quest_name, run_in_shell = arg_variant.unpack()
        self._window.clubhouse_page.run_quest_by_name(quest_name, run_in_shell)

    def _quit_action_cb(self, action, arg_variant):
        if self._window:
            self._window.destroy()
            self._window = None

        self.quit()

    def _show_page_action_cb(self, action, arg_variant):
        page_name = arg_variant.unpack()
        if self._window:
            self._window.set_page(page_name)
            self._show_and_focus_window()

    def _vibility_notify_cb(self, window, pspec):
        if self._window.is_visible():
            self.send_suggest_open(False)

        changed_props = {'Visible': GLib.Variant('b', self._window.is_visible())}
        variant = GLib.Variant.new_tuple(GLib.Variant('s', CLUBHOUSE_IFACE),
                                         GLib.Variant('a{sv}', changed_props),
                                         GLib.Variant('as', []))
        self.get_dbus_connection().emit_signal(None,
                                               CLUBHOUSE_PATH,
                                               'org.freedesktop.DBus.Properties',
                                               'PropertiesChanged',
                                               variant)

    def do_dbus_register(self, connection, path):
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

        invocation.return_value(getattr(self, method_name)(*args))

    def handle_get_property(self, connection, sender, object_path,
                            interface, key):
        if key == 'Visible':
            return GLib.Variant('b', self._window.is_visible() if self._window else False)
        elif key == 'SuggestingOpen':
            return GLib.Variant('b', self._suggesting_open)

        return None

    # D-Bus implementation
    def show(self, timestamp):
        self._ensure_window()
        self._show_and_focus_window(int(timestamp))

        return None

    # D-Bus implementation
    def hide(self, timestamp):
        if self._window:
            self._window.hide()

        return None

    def _show_and_focus_window(self, timestamp=None):
        # We deliberately show + present the window here to ensure it gets focused
        # when showing it after it's been hidden.
        self._window.show()
        self._window.present_with_time(timestamp if timestamp is not None else Gdk.CURRENT_TIME)

    # D-Bus implementation
    def getAnimationMetadata(self, uri):
        metadata_str = ''
        try:
            metadata_str = Animation.get_animation_metadata(uri, load_json=False)
        except Exception as e:
            logger.warning('Could not read metadata for animation: %s', e)

        metadata_variant = None
        try:
            metadata_variant = Json.gvariant_deserialize_data(metadata_str, -1, None)
        except Exception as e:
            logger.warning('Could not deserialize metadata for animation: %s', e)
            return None

        return GLib.Variant('(v)', (metadata_variant,))

    def _list_quests(self):
        self._ensure_registry_loaded()
        for quest_set in libquest.Registry.get_quest_sets():
            print(quest_set.get_id())
            for quest in quest_set.get_quests():
                print('\t{}'.format(quest.get_id()))

    def has_debug_mode(self):
        return self._debug_mode


if __name__ == '__main__':
    app = ClubhouseApplication()
    app.run(sys.argv)
