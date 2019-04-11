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
import functools
import json
import logging
import os
import subprocess
import sys
import time

from collections import OrderedDict
from gi.repository import Gdk, Gio, GLib, Gtk, GObject, Json
from eosclubhouse import config, logger, libquest, utils
from eosclubhouse.system import AccountService, Desktop, GameStateService, Sound
from eosclubhouse.utils import ClubhouseState, Performance, SimpleMarkupParser
from eosclubhouse.animation import Animation, AnimationImage, AnimationSystem, Animator, \
    get_character_animation_dirs

from eosclubhouse.episodes import BadgeButton


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
                  '<property name="RunningQuest" type="s" access="read"/>'
                  '<property name="SuggestingOpen" type="b" access="read"/>'
                  '</interface>'
                  '</node>')

DEFAULT_WINDOW_WIDTH = 480


class Character(GObject.GObject):
    _characters = {}
    DEFAULT_MOOD = 'talk'
    DEFAULT_BODY_ANIMATION = 'idle'

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
        self._body_animation = self.DEFAULT_BODY_ANIMATION
        self._body_image = None
        self._position = None
        self.load()

    def _get_id(self):
        return self._id

    def _get_mood(self):
        return self._mood

    def _set_mood(self, mood):
        if mood is None:
            mood = self.DEFAULT_MOOD
        self._mood = mood

    def _get_body_animation(self):
        return self._body_animation

    def _set_body_animation(self, body_animation):
        if body_animation is None:
            body_animation = self.DEFAULT_BODY_ANIMATION
        if body_animation == self._body_animation:
            return
        self._body_image.play(body_animation)
        self._body_animation = body_animation

    def get_body_image(self):
        return self._body_image

    def get_moods_path(self):
        return os.path.join(self._id, 'moods')

    def _get_mood_image(self, mood):
        mood_path = self.get_moods_path()
        for sprites_path in get_character_animation_dirs(mood_path):
            test_image = os.path.join(sprites_path, mood + '.png')
            if os.path.exists(test_image):
                return test_image
        raise ValueError()

    def get_mood_icon(self):
        mood_image = None
        try:
            mood_image = self._get_mood_image(self._mood)
        except ValueError:
            mood_image = self._get_mood_image(self.DEFAULT_MOOD)

        assert mood_image is not None, 'The default mood is not available!'
        image_file = Gio.File.new_for_path(mood_image)
        return Gio.FileIcon.new(image_file)

    def load(self):
        body_path = os.path.join(self._id, 'fullbody')
        self._load_position()
        self._body_image = AnimationImage(body_path)
        self._body_image.play('idle')

    def _load_position(self):
        checked_main_path = False

        for character_path in get_character_animation_dirs(self._id):
            conf_path = os.path.join(character_path, 'fullbody.json')
            conf_json = None

            try:
                with open(conf_path) as f:
                    conf_json = json.load(f)
            except FileNotFoundError:
                if not checked_main_path:
                    logger.debug('No conf for "%s" fullbody animation', self._id)
                continue
            finally:
                checked_main_path = True

            self._position = conf_json.get('position', None)
            if self._position is not None:
                self._position = tuple(self._position)

    def get_position(self):
        return self._position

    id = property(_get_id)
    mood = GObject.Property(_get_mood, _set_mood, type=str)
    body_animation = GObject.Property(_get_body_animation, _set_body_animation, type=str)


class Message(Gtk.Bin):

    __gsignals__ = {
        'closed': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
    }

    _LABEL_MARGIN = 70
    _MESSAGE_MARGIN = 49

    CHARACTER_HEIGHT = 155
    BUTTON_HEIGHT = 35
    LABEL_WIDTH = DEFAULT_WINDOW_WIDTH - _LABEL_MARGIN
    MESSAGE_HEIGHT = CHARACTER_HEIGHT + BUTTON_HEIGHT / 2 + _MESSAGE_MARGIN

    OPEN_DIALOG_SOUND = 'clubhouse/dialog/open'

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
            label_widget = button.get_children()[0].get_children()[0].get_children()[1]
            label_widget.set_property('valign', Gtk.Align.CENTER)

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
        self._character = Character.get_or_create(self._quest_set.get_character())

        image = self._character.get_body_image()
        image.show()
        self.add(image)

        self._set_highlighted(self._quest_set.highlighted)
        self._character.body_animation = self._quest_set.body_animation

        self._quest_set.connect('notify::highlighted', self._on_quest_set_highlighted_changed)
        self._quest_set.connect('notify::body-animation',
                                self._on_quest_set_body_animation_changed)

        # The button should only be visible when the QuestSet is visible
        self._quest_set.bind_property('visible', self, 'visible',
                                      GObject.BindingFlags.BIDIRECTIONAL |
                                      GObject.BindingFlags.SYNC_CREATE)

    def get_quest_set(self):
        return self._quest_set

    def _get_position(self):
        anchor = (0, 0)
        position = (0, 0)

        # Get the anchor (if any) so we adapt the position to it.
        if self._character:
            position = self._quest_set.get_position() or self._character.get_position() or position
            animation_image = self._character.get_body_image()
            if animation_image is not None:
                anchor = animation_image.get_anchor()

        return (position[0] - anchor[0], position[1] - anchor[1])

    def _on_quest_set_highlighted_changed(self, _quest_set, _param):
        self._set_highlighted(self._quest_set.highlighted)

    def _on_quest_set_body_animation_changed(self, _quest_set, _param):
        self._character.body_animation = self._quest_set.body_animation
        self.notify('position')

    def _set_highlighted(self, highlighted):
        highlighted_style = 'highlighted'
        style_context = self.get_style_context()
        if highlighted:
            style_context.add_class(highlighted_style)
        else:
            style_context.remove_class(highlighted_style)

    position = GObject.Property(_get_position, type=GObject.TYPE_PYOBJECT)


class ClubhousePage(Gtk.EventBox):

    class _QuestScheduleInfo:
        def __init__(self, quest, confirm_before, timeout, handler_id):
            self.quest = quest
            self.confirm_before = confirm_before
            self.timeout = timeout
            self.handler_id = handler_id

    def __init__(self, app_window):
        super().__init__(visible=True)

        self._current_quest = None
        self._scheduled_quest_info = None
        self._proposing_quest = False
        self._delayed_message_handler = 0

        self._last_user_answer = 0

        self._app_window = app_window
        self._app_window.connect('key-press-event', self._key_press_event_cb)
        self._app_window.connect('notify::visible', self._on_window_visibility_changed)

        self._app = self._app_window.get_application()
        assert self._app is not None

        self._setup_ui()
        self.get_style_context().add_class('clubhouse-page')
        self._reset_quest_actions()

        self._current_episode = None
        self._current_quest_notification = None

        self.add_tick_callback(AnimationSystem.step)

        self._gss = GameStateService()
        self._gss_hander_id = self._gss.connect('changed',
                                                lambda _gss: self._update_episode_if_needed())

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

    def _on_window_visibility_changed(self, _window, _param):
        if not self._app_window.props.visible:
            self._overlay_msg_box.hide()

    def _hide_message_overlay_cb(self, message):
        self._overlay_msg_box.hide()

    def _on_button_press_event_cb(self, main_box, event):
        if event.get_button().button == 1:
            self._message.close()
            return True

        return False

    def stop_quest(self):
        self._cancel_ongoing_task()
        self._reset_scheduled_quest()

    def quest_debug_skip(self):
        if self._current_quest is not None:
            self._current_quest.set_debug_skip(True)

    def _cancel_ongoing_task(self):
        if self._current_quest is None:
            return

        cancellable = self._current_quest.get_cancellable()
        if not cancellable.is_cancelled():
            logger.debug('Stopping quest %s', self._current_quest)
            cancellable.cancel()

        self._set_current_quest(None)

    def _on_button_position_changed(self, button, _param):
        self._main_characters_box.move(button, *button.position)

    def add_quest_set(self, quest_set):
        button = QuestSetButton(quest_set)
        quest_set.connect('notify::highlighted', self._on_quest_set_highlighted_changed)
        button.connect('clicked', self._button_clicked_cb)

        x, y = button.position
        self._main_characters_box.put(button, x, y)

        button.connect('notify::position', self._on_button_position_changed)

    def _on_quest_set_highlighted_changed(self, quest_set, _param):
        if self._app_window.is_visible():
            return

        self._app.send_suggest_open(libquest.Registry.has_quest_sets_highlighted())

    def _show_quest_continue_confirmation(self):
        if self._current_quest is None:
            return

        self._message.reset()
        self._message.set_character(self._current_quest.get_main_character())

        msg, continue_label, stop_label = self._current_quest.get_continue_info()
        self.show_message(msg,
                          [(continue_label, self._continue_quest, self._current_quest),
                           (stop_label, self._stop_quest_from_message, self._current_quest)])

        self._overlay_msg_box.show_all()

    def _stop_quest_from_message(self, quest):
        if self._is_current_quest(quest):
            self._cancel_ongoing_task()
            self._overlay_msg_box.hide()

    def _continue_quest(self, quest):
        if not self._is_current_quest(quest):
            return

        quest.set_to_foreground()
        self._shell_show_current_popup_message()
        self._app_window.hide()
        # Hide the message here because it may be showing from another quest set
        self._overlay_msg_box.hide()

    def _button_clicked_cb(self, button):
        quest_set = button.get_quest_set()
        self._message.reset()

        # If a quest from this quest_set is already running, then just hide the window so the
        # user focuses on the Shell's quest dialog
        if self._current_quest:
            if self._current_quest.available and self._current_quest in quest_set.get_quests() and \
               not self._current_quest.stopping:
                self._show_quest_continue_confirmation()
                return

        new_quest = quest_set.get_next_quest()
        character = new_quest.get_main_character() if new_quest else quest_set.get_character()
        self._message.set_character(character)

        self._stop_quest_proposal()

        if new_quest is None:
            msg_text = quest_set.get_empty_message()
            # If a QuestSet has overridden the empty message to be None, then don't
            # show anything
            if msg_text is None:
                return

            self.show_message(msg_text, [('Ok', self._message.close)])
        else:
            sfx_sound = new_quest.get_initial_sfx_sound()
            self.show_message(new_quest.get_initial_message(),
                              [(new_quest.accept_label, self._accept_quest_message, quest_set,
                                new_quest),
                               (new_quest.reject_label, self._message.close)],
                              sfx_sound)

        self._overlay_msg_box.show_all()

    def _stop_quest_proposal(self):
        if self._proposing_quest:
            self._shell_close_popup_message()
            self._proposing_quest = False

    def _accept_quest_message(self, quest_set, new_quest):
        self._message.hide()
        self._overlay_msg_box.hide()
        logger.info('Start quest {}'.format(new_quest))
        quest_set.set_property('highlighted', False)
        self.run_quest(new_quest)

    def connect_quest(self, quest):
        # Don't update the episode if we're running a quest; this is so we avoid reloading the
        # Clubhouse while running a quest if it changes the episode.
        self._gss.handler_block(self._gss_hander_id)

        quest.connect('message', self._quest_message_cb)
        quest.connect('schedule-quest', self._quest_scheduled_cb)
        quest.connect('item-given', self._quest_item_given_cb)

    def disconnect_quest(self, quest):
        self._gss.handler_unblock(self._gss_hander_id)
        quest.disconnect_by_func(self._quest_message_cb)
        quest.disconnect_by_func(self._quest_scheduled_cb)
        quest.disconnect_by_func(self._quest_item_given_cb)

    def run_quest(self, quest):
        self._stop_quest_proposal()

        # Stop any scheduled quests from attempting to run if we are running a quest
        self._reset_scheduled_quest()

        # Ensure the app stays alive at least for as long as we're running the quest
        self._app.hold()

        self._cancel_ongoing_task()

        # Start running the new quest only when the mainloop is idle so we allow any previous
        # events (from other quests) to be dispatched.
        GLib.idle_add(self._run_new_quest, quest)

    def _run_new_quest(self, quest):
        logger.info('Running quest "%s"', quest)

        self.connect_quest(quest)

        quest.set_cancellable(Gio.Cancellable())

        self._set_current_quest(quest)

        # Hide the window so the user focuses on the Shell Quest View
        self._app_window.hide()

        self._current_quest.run(self.on_quest_finished)
        return GLib.SOURCE_REMOVE

    def run_quest_by_name(self, quest_name):
        quest = libquest.Registry.get_quest_by_name(quest_name)
        if quest is None:
            logger.warning('No quest with name "%s" found!', quest_name)
            return

        if self._is_current_quest(quest):
            logger.warning('Quest "%s" is already being run!', quest_name)
            return

        self._cancel_ongoing_task()

        self.run_quest(quest)

    def _is_current_quest(self, quest):
        return self._current_quest is not None and self._current_quest == quest

    def _quest_scheduled_cb(self, quest, quest_name, confirm_before, start_after_timeout):
        self._reset_scheduled_quest()

        # This means that scheduling a quest called '' just removes the scheduled quest
        if not quest_name:
            return

        quest = libquest.Registry.get_quest_by_name(quest_name)
        if quest is None:
            logger.warning('No quest with name "%s" found when setting up next quest from '
                           'running quest "%s"!', quest_name, quest.get_id())
            return

        self._scheduled_quest_info = self._QuestScheduleInfo(quest, confirm_before,
                                                             start_after_timeout, 0)

    def _quest_item_given_cb(self, quest, item_id, text):
        self._shell_popup_item(item_id, text)

    def _quest_message_cb(self, quest, message_txt, answer_choices, character_id, character_mood,
                          sfx_sound, bg_sound):
        logger.debug('Message: %s character_id=%s mood=%s choices=[%s]', message_txt, character_id,
                     character_mood, '|'.join([answer for answer, _cb, *_args in answer_choices]))

        self._reset_quest_actions()

        for answer in answer_choices:
            self._add_quest_action(answer)

        character = Character.get_or_create(character_id)
        character.mood = character_mood

        self._shell_popup_message(message_txt, character, sfx_sound, bg_sound)

    def _reset_delayed_message(self):
        if self._delayed_message_handler > 0:
            GLib.source_remove(self._delayed_message_handler)
            self._delayed_message_handler = 0

    def on_quest_finished(self, quest):
        logger.debug('Quest {} finished'.format(quest))
        self.disconnect_quest(quest)
        self._reset_delayed_message()
        quest.save_conf()
        quest.dismiss()

        # Ensure we reset the running quest (only if we haven't started a different quest in the
        # meanwhile) quest and close any eventual message popups
        if self._is_current_quest(quest):
            self._set_current_quest(None)

        if self._current_quest is None:
            self._shell_close_popup_message()

        self._current_quest_notification = None

        self._update_episode_if_needed()

        # Ensure the app can be quit if inactive now
        self._app.release()

        # If there is a next quest to run, we start it
        self._schedule_next_quest()

    def _reset_scheduled_quest(self):
        if self._scheduled_quest_info is not None:
            if self._scheduled_quest_info.handler_id > 0:
                GLib.source_remove(self._scheduled_quest_info.handler_id)
                self._scheduled_quest_info.handler_id = 0

            self._scheduled_quest_info = None

    def _schedule_next_quest(self):
        if self._scheduled_quest_info is None:
            return

        def _run_quest_after_timeout():
            if self._scheduled_quest_info is None:
                return

            quest = self._scheduled_quest_info.quest
            confirm_before = self._scheduled_quest_info.confirm_before

            self._reset_scheduled_quest()

            if confirm_before:
                self._propose_next_quest(quest)
            else:
                self.run_quest(quest)

            return GLib.SOURCE_REMOVE

        timeout = self._scheduled_quest_info.timeout
        self._scheduled_quest_info.handler_id = GLib.timeout_add_seconds(timeout,
                                                                         _run_quest_after_timeout)

    def _propose_next_quest(self, quest):
        quest_set = quest.quest_set
        character_id = quest.get_main_character()
        if not character_id and quest.quest_set is not None:
            character_id = quest_set.get_character()

        self._reset_quest_actions()

        for answer in [(quest.accept_label, self._accept_quest_message, quest_set, quest),
                       (quest.reject_label, self._stop_quest_proposal)]:
            self._add_quest_action(answer)

        sfx_sound = quest.get_initial_sfx_sound()
        character = Character.get_or_create(character_id)

        self._proposing_quest = True
        self._shell_popup_message(quest.get_initial_message(), character, sfx_sound, None)

    def _key_press_event_cb(self, window, event):
        # Allow to fully quit the Clubhouse on Ctrl+Escape
        if event.keyval == Gdk.KEY_Escape and (event.state & Gdk.ModifierType.CONTROL_MASK):
            self._app_window.destroy()
            return True

        if self._current_quest:
            event_copy = event.copy()
            self._current_quest.on_key_event(event_copy)

        return False

    def _shell_close_popup_message(self):
        self._app.close_quest_msg_notification()

    def _shell_popup_message(self, text, character, sfx_sound, bg_sound):
        real_popup_message = functools.partial(self._shell_popup_message_real, text, character,
                                               sfx_sound, bg_sound)

        # If the user last interacted with a notification longer than a second ago, then we delay
        # the new notification a bit. The delaying is so that it is more noticeable to the user
        # that the notification has changed; the "last time" check is so we don't delay if the
        # new notification is a result of a user recent interaction.
        if time.time() - self._last_user_answer > 1:
            self._app.withdraw_notification(self._app.QUEST_MSG_NOTIFICATION_ID)
            self._reset_delayed_message()
            self._delayed_message_handler = GLib.timeout_add(300, real_popup_message)
        else:
            real_popup_message()

    def _shell_popup_message_real(self, text, character, sfx_sound, bg_sound):
        notification = Gio.Notification()
        notification.set_body(SimpleMarkupParser.parse(text))
        notification.set_title('')

        if sfx_sound:
            Sound.play(sfx_sound)
        if self._current_quest and bg_sound != self._current_quest.get_last_bg_sound_event_id():
            self._current_quest.play_stop_bg_sound(bg_sound)

        if character:
            notification.set_icon(character.get_mood_icon())
            Sound.play('clubhouse/{}/mood/{}'.format(character.id,
                                                     character.mood))

        for key, action in self._actions.items():
            label = action[0]
            button_target = "app.quest-user-answer('{}')".format(key)
            notification.add_button(label, button_target)

        # Add debug button (e.g. to quickly skip steps)
        if self._app.has_debug_mode():
            notification.add_button('🐞', 'app.quest-debug-skip')

        self._app.send_quest_msg_notification(notification)
        self._current_quest_notification = (notification, sfx_sound)

        self._delayed_message_handler = 0
        return GLib.SOURCE_REMOVE

    def _shell_show_current_popup_message(self):
        if self._current_quest_notification is None:
            return

        notification, sound = self._current_quest_notification

        if sound:
            Sound.play(sound)

        self._app.send_quest_msg_notification(notification)

    def _shell_popup_item(self, item_id, text):
        item = utils.QuestItemDB.get_item(item_id)
        if item is None:
            logger.debug('Failed to get item %s from DB', item_id)
            return

        icon_name, _icon_used_name, item_name = item[:3]

        notification = Gio.Notification()
        if text is None:
            text = 'You got a new item! {}'.format(item_name)

        notification.set_body(SimpleMarkupParser.parse(text))
        notification.set_title('')

        icon_file = Gio.File.new_for_path(utils.QuestItemDB.get_icon_path(icon_name))
        icon_bytes = icon_file.load_bytes(None)
        icon = Gio.BytesIcon.new(icon_bytes[0])

        notification.set_icon(icon)

        notification.add_button('OK', 'app.item-accept-answer(false)')
        notification.add_button('Show me', 'app.item-accept-answer(true)')

        Sound.play('quests/key-given')

        self._app.send_quest_item_notification(notification)

    def show_message(self, txt, answer_choices=[], sfx_sound=None):
        self._message.clear_buttons()
        self._message.set_text(txt)

        for answer in answer_choices:
            self._message.add_button(answer[0], *answer[1:])

        # @todo: bg sounds are not supported yet.
        if not sfx_sound:
            sfx_sound = self._message.OPEN_DIALOG_SOUND
        Sound.play(sfx_sound)

        return self._message

    def _reset_quest_actions(self):
        # We need to maintain the order of the quest actions, so we use an OrderedDict here.
        self._actions = OrderedDict()

    def _add_quest_action(self, action):
        # Lazy import UUID module because it takes a while to do so, and we only need it here
        import uuid

        key = str(uuid.uuid1())
        self._actions[key] = action
        return key

    def quest_action(self, action_key):
        actions = self._actions
        action = self._actions.get(action_key)

        if action is None:
            logger.debug('Failed to get action for key %s', action_key)
            logger.debug('Current actions: %s', actions)
            return

        # It's important to reset the quest actions only after the check above, as the same action
        # can be triggered twice by clicking the Quest view button's very quickly, and in that case,
        # the second time we could be resetting the actions when new ones have been added by the
        # quests in the meanwhile.
        self._reset_quest_actions()

        # Call the action
        callback, args = action[1], action[2:]
        callback(*args)

        self._last_user_answer = time.time()

    def set_quest_to_background(self):
        if self._current_quest:
            self._current_quest.set_to_background()
        else:
            # If the quest proposal dialog in the Shell has been dismissed, then we
            # should reset the "proposing_quest" flag.
            self._stop_quest_proposal()

    def _get_running_quest(self):
        if self._current_quest is None:
            return None
        return self._current_quest

    def _set_current_quest(self, quest_obj):
        if quest_obj is not self._current_quest:
            self._current_quest = quest_obj
            self.notify('running-quest')

    def load_episode(self, episode_name=None):
        self._cancel_ongoing_task()

        if episode_name is None:
            episode_name = libquest.Registry.get_current_episode()['name']
        self._current_episode = episode_name

        for child in self._main_characters_box.get_children():
            child.destroy()

        libquest.Registry.load_current_episode()
        for quest_set in libquest.Registry.get_quest_sets():
            self.add_quest_set(quest_set)

    def _update_episode_if_needed(self):
        episode_name = libquest.Registry.get_current_episode()['name']
        if self._current_episode != episode_name:
            self.load_episode(episode_name)

    running_quest = GObject.Property(_get_running_quest,
                                     type=GObject.TYPE_PYOBJECT,
                                     default=None,
                                     flags=GObject.ParamFlags.READABLE |
                                     GObject.ParamFlags.EXPLICIT_NOTIFY)


class InventoryItem(Gtk.Button):

    _ITEM_WIDTH = 150
    _ITEM_HEIGHT = 265

    def __init__(self, item_id, is_used, icon_name, icon_used_name, item_name,
                 item_description):
        super().__init__(height_request=self._ITEM_HEIGHT)

        self.item_id = item_id
        self.item_name = item_name
        self.is_used = is_used
        self._icon_name = icon_name
        self._icon_used_name = icon_used_name
        self._description = item_description

        self.get_style_context().add_class('inventory-item')

        self.connect('clicked', self._on_item_clicked_cb)

        vbox = Gtk.Box(width_request=self._ITEM_WIDTH,
                       halign=Gtk.Align.FILL,
                       orientation=Gtk.Orientation.VERTICAL,
                       spacing=16)
        self.add(vbox)

        self._image = Gtk.Image()
        vbox.add(self._image)

        self._label = Gtk.Label(wrap=True,
                                max_width_chars=15,
                                hexpand=False,
                                halign=Gtk.Align.CENTER,
                                justify=Gtk.Justification.CENTER)
        self._label.set_text(item_name)

        vbox.add(self._label)
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

    def _is_key(self):
        return self.item_id.startswith('item.key.')

    def _on_item_clicked_cb(self, *_args):
        self.get_style_context().add_class('active')
        text = self._description

        if not text:
            if not self._is_key():
                text = 'This is a special item.'
            elif self.is_used:
                text = 'This key has already been used.'
            else:
                text = 'To use this key click on the matching lock.'

        self._label.set_text(text)
        GLib.timeout_add_seconds(5, self._deactivate_on_timeout)

    def _deactivate_on_timeout(self):
        self.get_style_context().remove_class('active')
        self._label.set_text(self.item_name)


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

    def _add_item(self, item_id, is_used, icon_name, icon_used_name, item_name, item_description):
        if item_id in self._loaded_items:
            item = self._loaded_items[item_id]
            item.set_used(is_used)
            return

        new_item = InventoryItem(item_id, is_used, icon_name, icon_used_name, item_name,
                                 item_description)
        self._loaded_items[item_id] = new_item
        self._inventory_box.add(new_item)

    def _remove_item(self, item_id):
        item = self._loaded_items.get(item_id)
        if item:
            self._inventory_box.remove(item.get_parent())
            del self._loaded_items[item_id]

    def _load_items(self):
        # For now there is no method in the GameStateService to retrieve items based
        # on a prefix, so every time there's a change in the service, we need to directly
        # verify all the items we're interested in.
        for item_id, (icon, icon_used, name, description) in self._items_db.get_all_items():
            item_state = self._gss.get(item_id)
            if item_state is None:
                self._remove_item(item_id)
                continue

            # Used items shouldn't show up in the inventory if are consume-able
            if (item_state.get('used', False) and
               item_state.get('consume_after_use', False)):
                self._remove_item(item_id)
                continue

            is_used = item_state.get('used', False)
            self._add_item(item_id, is_used, icon, icon_used, name, description.strip())

        self._update_state()

    def _update_state(self):
        if len(self._loaded_items) > 0:
            self._inventory_stack.set_visible_child(self._inventory_box)
        else:
            self._inventory_stack.set_visible_child(self._inventory_empty_state_box)


class EpisodesPage(Gtk.EventBox):

    _COMPLETED = 'completed'

    def __init__(self, app_window):
        super().__init__(visible=True)

        self._episodes_db = utils.EpisodesDB()

        self._app_window = app_window
        self._current_page = None
        self._current_episode = None
        self._badges = {}
        self._setup_ui()
        GameStateService().connect('changed', self.update_episode_view)
        self.update_episode_view()

    def _setup_ui(self):
        self.get_style_context().add_class('episodes-page')

        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/episodes-page.ui')

        self._badges_box = builder.get_object('badges_box')

        self.add(self._badges_box)

    def _update_ui(self, new_page):
        if new_page == self._current_page:
            return

        # remove old episode background
        episode = self._current_episode
        if episode:
            self.get_style_context().remove_class(episode['name'])

        for child in self._badges_box.get_children():
            self._badges_box.remove(child)

        if self._current_page is not None:
            self.get_style_context().remove_class(self._current_page)
        self._current_page = new_page
        self.get_style_context().add_class(self._current_page)

        current_episode = libquest.Registry.get_current_episode()
        if new_page == self._COMPLETED:
            self.get_style_context().add_class(current_episode['name'])
        episode = self._episodes_db.get_episode(current_episode['name'])

        # draw completed episodes
        completed_episodes = self._episodes_db.get_previous_episodes(episode.id)
        for completed in completed_episodes:
            self._add_badge_button(completed,
                                   completed.badge_x,
                                   completed.badge_y)

        if new_page == self._COMPLETED:
            x, y = episode.badge_x, episode.badge_y
            if not completed_episodes:
                x = DEFAULT_WINDOW_WIDTH / 2
            self._add_badge_button(episode, x, y)

    def _add_badge_button(self, episode, x, y):
        badge = BadgeButton(episode)
        self._badges[episode.id] = badge

        w, _h = badge.get_size()
        x -= w / 2

        self._badges_box.put(badge, x, y)
        badge.show()

    def update_episode_view(self, _gss=None):
        current_episode = libquest.Registry.get_current_episode()
        if current_episode[self._COMPLETED]:
            self._update_ui(self._COMPLETED)
        else:
            self._update_ui(current_episode['name'])

        self._update_episode_badges()

    def click_badge(self, episode):
        button = self._badges.get(episode)

        if not button:
            return

        button.clicked()

    def _update_episode_badges(self, _gss=None):
        current_episode = libquest.Registry.get_current_episode()

        if self._current_episode == current_episode:
            return

        is_same_episode = False
        if self._current_episode is None or \
           self._current_episode['name'] == current_episode['name']:
            self._current_episode = current_episode
            is_same_episode = True

        episode_name = self._current_episode['name']
        is_teaser_viewed = self._current_episode['teaser-viewed']

        # We want to show the teaser if it hasn't been viewed yet.
        show = not is_teaser_viewed

        # If there's been an episode transition, then we just check if the teaser hasn't been
        # viewed in order to show it; otherwise, if the episode is the current one, then we also
        # check if it's complete.
        if not is_same_episode:
            # Ensure we update the current episode info.
            self._current_episode = current_episode
            show = not is_teaser_viewed
        else:
            show = self._current_episode[self._COMPLETED] and not is_teaser_viewed

        if show:
            self.click_badge(episode_name)

        # Only update the teaser-viewed info if there hasn't been an episode change.
        if is_same_episode:
            libquest.Registry.set_current_episode_teaser_viewed(True)


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

        self._clubhouse_state = ClubhouseState()

    def _setup_ui(self):
        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/main-window.ui')

        self._main_window_stack = builder.get_object('main_window_stack')

        self._clubhouse_button = builder.get_object('main_window_button_clubhouse')
        self._inventory_button = builder.get_object('main_window_button_inventory')
        self._episodes_button = builder.get_object('main_window_button_episodes')

        pages_data = [(self._clubhouse_button, ClubhouseState.Page.CLUBHOUSE, self.clubhouse_page),
                      (self._inventory_button, ClubhouseState.Page.INVENTORY, self.inventory_page),
                      (self._episodes_button, ClubhouseState.Page.EPISODES, self.episodes_page)]

        for button, page_id, page_widget in pages_data:
            self._main_window_stack.add_named(page_widget, page_id.name)
            button.connect('clicked', self._page_switch_button_clicked_cb, page_id)

        self.add(builder.get_object('main_window_overlay'))

    def _window_realize_cb(self, window):
        def _window_focus_out_event_cb(_window, _event):
            self.hide()
            return False

        gdk_window = self.get_window()
        gdk_window.set_functions(0)
        gdk_window.set_events(gdk_window.get_events() | Gdk.EventMask.FOCUS_CHANGE_MASK)

        if os.environ.get('CLUBHOUSE_NO_AUTO_HIDE') is None:
            self.connect('focus-out-event', _window_focus_out_event_cb)

    def _page_switch_button_clicked_cb(self, button, page_id):
        self._main_window_stack.set_visible_child_name(page_id.name)
        self._clubhouse_state.current_page = page_id

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

        self._clubhouse_state.window_is_visible = self.props.visible

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

    _INACTIVITY_TIMEOUT = 5 * 60 * 1000  # millisecs

    def __init__(self):
        super().__init__(application_id=CLUBHOUSE_NAME,
                         inactivity_timeout=self._INACTIVITY_TIMEOUT,
                         resource_base_path='/com/endlessm/Clubhouse')

        self._window = None
        self._debug_mode = False
        self._registry_loaded = False
        self._suggesting_open = False
        self._session_mode = None

        resource = Gio.resource_load(os.path.join(config.DATA_DIR, 'eos-clubhouse.gresource'))
        Gio.Resource._register(resource)

        self.add_main_option('list-quests', ord('q'), GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'List existing quest sets and quests', None)
        self.add_main_option('list-episodes', 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'List available episodes', None)
        self.add_main_option('get-episode', 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'Print the current episode', None)
        self.add_main_option('set-episode', 0, GLib.OptionFlags.NONE, GLib.OptionArg.STRING,
                             'Switch to this episode, marking it as not complete', 'EPISODE_NAME')
        self.add_main_option('reset', 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'Reset all quests state and game progress', None)
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

    def _run_episode_autorun_quest_if_needed(self):
        def _run_autorun_quest_if_user_session(proxy=None):
            if proxy is not None:
                self._session_mode = proxy.get_cached_property('Mode').unpack()

            assert self._session_mode is not None, 'Session mode not set up'

            # Restrict the autorun quest to only normal sessions (since we don't want to auto-run
            # quests in the initial setup and other cases)
            if self._session_mode != 'user':
                return

            autorun_quest = libquest.Registry.get_autorun_quest()
            if autorun_quest is None:
                return

            quest = libquest.Registry.get_quest_by_name(autorun_quest)
            if not quest.complete:
                # Run the quest in the app's main instance
                self.activate_action('run-quest', GLib.Variant('(sb)', (autorun_quest, True)))

        if self._session_mode is None:
            Desktop.get_shell_proxy_async(_run_autorun_quest_if_user_session)
        else:
            _run_autorun_quest_if_user_session()

    def do_handle_local_options(self, options):
        self.register(None)

        if options.contains('list-quests'):
            self._list_quests()
            return 0

        if options.contains('list-episodes'):
            available_episodes = libquest.Registry.get_available_episodes()
            for episode in available_episodes:
                print(episode)
            return 0

        if options.contains('get-episode'):
            current_episode = libquest.Registry.get_current_episode()
            print(current_episode['name'])
            return 0

        if options.contains('set-episode'):
            self.activate_action('quit', None)
            episode_value = options.lookup_value('set-episode', GLib.VariantType('s'))
            episode_name = episode_value.get_string()
            available_episodes = libquest.Registry.get_available_episodes()
            if episode_name not in available_episodes:
                logger.error('Episode %s is not available.', episode_name)
                return 1

            GameStateService().reset()
            libquest.Registry.set_current_episode(episode_name)
            return 0

        if options.contains('reset'):
            self.activate_action('quit', None)
            return self._reset()

        if options.contains('debug'):
            self.activate_action('debug-mode', GLib.Variant('b', True))
            # We still try to run the Episode's auto-run quest since this option is only be
            # called for turning the debug mode on (as opposed to other options that have an
            # end functionality on their own).
            self._run_episode_autorun_quest_if_needed()
            return 0

        if options.contains('quit'):
            self.activate_action('quit', None)
            return 0

        # We call this here, instead of the startup method since we want to avoid eventually
        # running a quest if the application is only being started for any of the options above
        # (except for debug).
        self._run_episode_autorun_quest_if_needed()

        return -1

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self._ensure_registry_loaded()
        self._ensure_suggesting_open()
        self._init_style()

        simple_actions = [('debug-mode', self._debug_mode_action_cb, GLib.VariantType.new('b')),
                          ('item-accept-answer', self._item_accept_action_cb,
                           GLib.VariantType.new('b')),
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

        # Make sure that we create a user account if there's none
        AccountService().init_accounts()

    def _ensure_registry_loaded(self):
        if not self._registry_loaded:
            libquest.Registry.load_current_episode()
            self._registry_loaded = True

    def _ensure_suggesting_open(self):
        quest_sets = libquest.Registry.get_quest_sets()
        for quest_set in quest_sets:
            if quest_set.highlighted:
                self.send_suggest_open(True)
                break

    def _ensure_window(self):
        if self._window:
            return

        self._window = ClubhouseWindow(self)
        self._window.connect('notify::visible', self._visibility_notify_cb)
        self._window.clubhouse_page.connect('notify::running-quest',
                                            self._running_quest_notify_cb)

        self._window.clubhouse_page.load_episode()

    def send_quest_msg_notification(self, notification):
        self.send_notification(self.QUEST_MSG_NOTIFICATION_ID, notification)

    def close_quest_msg_notification(self):
        self.withdraw_notification(self.QUEST_MSG_NOTIFICATION_ID)

    def send_quest_item_notification(self, notification):
        self.send_notification(self.QUEST_ITEM_NOTIFICATION_ID, notification)

    def close_quest_item_notification(self):
        self.withdraw_notification(self.QUEST_ITEM_NOTIFICATION_ID)

    def _emit_dbus_props_changed(self, changed_props):
        variant = GLib.Variant.new_tuple(GLib.Variant('s', CLUBHOUSE_IFACE),
                                         GLib.Variant('a{sv}', changed_props),
                                         GLib.Variant('as', []))
        self.get_dbus_connection().emit_signal(None,
                                               CLUBHOUSE_PATH,
                                               'org.freedesktop.DBus.Properties',
                                               'PropertiesChanged',
                                               variant)

    def send_suggest_open(self, suggest):
        if suggest == self._suggesting_open:
            return

        self._suggesting_open = suggest
        changed_props = {'SuggestingOpen': GLib.Variant('b', self._suggesting_open)}
        self._emit_dbus_props_changed(changed_props)

    def _stop_quest(self, *args):
        if (self._window):
            self._window.clubhouse_page.stop_quest()
        self.close_quest_msg_notification()

    def _item_accept_action_cb(self, action, arg_variant):
        Sound.play('quests/key-confirm')
        show_inventory = arg_variant.unpack()
        if show_inventory and self._window:
            self._window.set_page('inventory')
            self._show_and_focus_window()

    def _debug_mode_action_cb(self, action, arg_variant):
        # Add debugging information in the Application UI:
        self._debug_mode = arg_variant.unpack()
        self._ensure_window()

        # Also set the logging level:
        logger.setLevel(logging.DEBUG)

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

    def _run_quest_by_name(self, quest_name):
        self._ensure_window()
        self._window.clubhouse_page.run_quest_by_name(quest_name)

    def _run_quest_action_cb(self, action, arg_variant):
        quest_name, _obsolete = arg_variant.unpack()
        self._run_quest_by_name(quest_name)

    def _quit_action_cb(self, action, arg_variant):
        self._stop_quest()

        if self._window:
            self._window.destroy()
            self._window = None

        self.quit()

    def _show_page_action_cb(self, action, arg_variant):
        page_name = arg_variant.unpack()
        if self._window:
            self._window.set_page(page_name)
            self._show_and_focus_window()

    def _visibility_notify_cb(self, window, pspec):
        if self._window.is_visible():
            # Manage the application's inactivity manually
            self.add_window(self._window)

            self.send_suggest_open(False)
        else:
            # Manage the application's inactivity manually
            self.remove_window(self._window)

        changed_props = {'Visible': GLib.Variant('b', self._window.is_visible())}
        self._emit_dbus_props_changed(changed_props)

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
        elif key == 'RunningQuest':
            return GLib.Variant('s', self._get_running_quest_name())

        return None

    def _running_quest_notify_cb(self, _clubhouse_page, _pspec):
        changed_props = {'RunningQuest': GLib.Variant('s', self._get_running_quest_name())}
        self._emit_dbus_props_changed(changed_props)

    def _get_running_quest_name(self):
        if self._window is not None:
            quest = self._window.clubhouse_page.props.running_quest
            if quest is not None:
                return quest.get_id()
        return ''

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
        for quest_set in libquest.Registry.get_quest_sets():
            print(quest_set.get_id())
            for quest in quest_set.get_quests():
                print('\t{}'.format(quest.get_id()))

    def _reset(self):
        try:
            subprocess.run(config.RESET_SCRIPT_PATH, check=True)
            return 0
        except subprocess.CalledProcessError as e:
            logger.warning('Could not reset the Clubhouse: %s', e)
            return 1

    def has_debug_mode(self):
        return self._debug_mode


if __name__ == '__main__':
    app = ClubhouseApplication()
    app.run(sys.argv)
