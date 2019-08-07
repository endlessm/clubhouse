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
from eosclubhouse.system import Desktop, GameStateService, Sound
from eosclubhouse.utils import ClubhouseState, Performance, SimpleMarkupParser
from eosclubhouse.animation import Animation, AnimationImage, AnimationSystem, Animator, \
    get_character_animation_dirs

from eosclubhouse.episodes import BadgeButton, PosterWindow


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

# Load Resources
resource = Gio.resource_load(os.path.join(config.DATA_DIR, 'eos-clubhouse.gresource'))
Gio.Resource._register(resource)


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

    def load(self, scale=1):
        body_path = os.path.join(self._id, 'fullbody')
        self._load_position()
        self._body_image = AnimationImage(body_path, scale)
        self._body_image.play(self.DEFAULT_BODY_ANIMATION)

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


@Gtk.Template.from_resource('/com/endlessm/Clubhouse/message.ui')
class Message(Gtk.Overlay):

    __gtype_name__ = 'Message'

    __gsignals__ = {
        'closed': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
    }

    _label = Gtk.Template.Child()
    _character_image = Gtk.Template.Child()
    _button_box = Gtk.Template.Child()
    close_button = Gtk.Template.Child()

    OPEN_DIALOG_SOUND = 'clubhouse/dialog/open'

    def __init__(self):
        super().__init__()
        self._character = None
        self._character_mood_change_handler = 0
        self._animator = Animator(self._character_image)
        self.connect("show", lambda _: Sound.play('clubhouse/dialog/open'))

    @Gtk.Template.Callback()
    def _close_button_clicked_cb(self, button):
        self.close()

    def set_text(self, txt):
        self._label.set_markup(SimpleMarkupParser.parse(txt))

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

    def display_character(self, display):
        self._character_image.props.visible = display

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

    def update(self, message_info):
        self.reset()
        self.set_text(message_info.get('text', ''))
        self.set_character(message_info.get('character_id'))

        for answer in message_info.get('choices', []):
            self.add_button(answer[0], *answer[1:])

        # @todo: bg sounds are not supported yet.
        sfx_sound = message_info.get('sound_fx')
        if not sfx_sound:
            sfx_sound = self.OPEN_DIALOG_SOUND
        Sound.play(sfx_sound)


class QuestButton(Gtk.Button):

    _LABEL_FOR_DIFFICULTY = {
        libquest.Quest.Difficulty.EASY: '★☆☆',
        libquest.Quest.Difficulty.NORMAL: '★★☆',
        libquest.Quest.Difficulty.HARD: '★★★',
    }

    def __init__(self, quest):
        super().__init__(label=self._get_label(quest))

        self.get_style_context().add_class('quest-button')

        self._quest = quest
        self._quest.connect('notify::complete', self._on_quest_complete_changed)
        self._set_complete()

    def _on_quest_complete_changed(self, _quest_set, _param):
        self._set_complete()

    def _set_complete(self):
        complete_style = 'complete'
        style_context = self.get_style_context()
        if self._quest.complete:
            style_context.add_class(complete_style)
        else:
            style_context.remove_class(complete_style)

    def _get_label(self, quest):
        difficulty = self._LABEL_FOR_DIFFICULTY[quest.get_difficulty()]
        return quest.get_name() + ' - difficulty: ' + difficulty

    def get_quest(self):
        return self._quest


class CharacterMissionButton(QuestButton):
    def __init__(self, quest_set, quest):
        super().__init__(quest)

        self._quest_set = quest_set

    def get_quest_set(self):
        return self._quest_set


class QuestSetButton(Gtk.Button):

    def __init__(self, quest_set, scale=1):
        super().__init__(halign=Gtk.Align.START,
                         relief=Gtk.ReliefStyle.NONE)

        self.get_style_context().add_class('quest-set-button')

        self._quest_set = quest_set
        self._character = Character.get_or_create(self._quest_set.get_character())
        self.reload(scale)

        self._set_highlighted(self._quest_set.highlighted)
        self._character.body_animation = self._quest_set.body_animation

        self.connect('clicked', self._on_button_clicked_cb)
        self._quest_set.connect('notify::highlighted', self._on_quest_set_highlighted_changed)
        self._quest_set.connect('notify::body-animation',
                                self._on_quest_set_body_animation_changed)

        # The button should only be visible when the QuestSet is visible
        self._quest_set.bind_property('visible', self, 'visible',
                                      GObject.BindingFlags.BIDIRECTIONAL |
                                      GObject.BindingFlags.SYNC_CREATE)
        self._quest_set.bind_property('body-animation', self._character, 'body-animation',
                                      GObject.BindingFlags.SYNC_CREATE)
        Desktop.shell_settings_bind(Desktop.SETTINGS_HACK_MODE_KEY, self, 'sensitive')

    def reload(self, scale):
        self._scale = scale
        self._character.load(scale)

        child = self.get_child()
        if child is not None:
            self.remove(child)

        image = self._character.get_body_image()
        self.add(image)
        image.show()

        self.notify('position')

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

        return ((position[0] - anchor[0]) * self._scale,
                (position[1] - anchor[1]) * self._scale)

    def _on_button_clicked_cb(self, _button):
        if self._quest_set.highlighted:
            self._quest_set.highlighted = False

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


@Gtk.Template.from_resource('/com/endlessm/Clubhouse/character-view.ui')
class CharacterView(Gtk.Grid):

    __gtype_name__ = 'CharacterView'

    MAX_MESSAGES = 2
    MIN_MESSAGE_WIDTH = 320
    MIN_MESSAGE_WIDTH_RATIO = 0.8

    header_box = Gtk.Template.Child()
    _list = Gtk.Template.Child()
    _character_overlay = Gtk.Template.Child()
    _character_image = Gtk.Template.Child()
    _character_button = Gtk.Template.Child()
    _message_list = Gtk.Template.Child()

    def __init__(self, app_window):
        super().__init__(visible=True)
        self._app_window = app_window
        self._animator = Animator(self._character_image)
        self._character = None
        self._scale = 1

    def _update_character_image(self):
        if self._character is None:
            return

        animation_id = self._character.id + '/closeup-talk'
        if not self._animator.has_animation(animation_id) or \
           self._animator.get_animation_scale(animation_id) != self._scale:
            self._animator.load(self._character.get_moods_path(),
                                self._character.id,
                                self._scale)

        # @todo: play animation only when a dialog is added
        self._animator.play(animation_id)

    def set_scale(self, scale):
        self._scale = scale
        self._update_character_image()

    def add_message(self, message_info):
        current_quest = self._app_window.clubhouse._get_running_quest()
        if not current_quest:
            return

        if len(self._message_list.get_children()) == self.MAX_MESSAGES:
            row = self._message_list.get_row_at_index(0)
            self._message_list.remove(row)

        msg = Message()
        msg.update(message_info)
        self._message_list.add(msg)

        overlay_width = self._character_overlay.get_allocation().width
        msg.props.width_request = \
            min(overlay_width, max(self.MIN_MESSAGE_WIDTH,
                                   overlay_width * self.MIN_MESSAGE_WIDTH_RATIO))

        if message_info.get('character_id') == current_quest.get_main_character():
            msg.display_character(False)
            msg.props.halign = Gtk.Align.START
        else:
            msg.display_character(True)
            msg.props.halign = Gtk.Align.END

        return msg

    def clear_messages(self):
        for row in self._message_list.get_children():
            self._message_list.remove(row)

    def show_mission_list(self, quest_set):
        # Get character
        self._character = Character.get_or_create(quest_set.get_character())

        # Set page title
        self._character_button.set_label(self._character.id.capitalize() + '\'s Workshop')

        # Set character image
        self._update_character_image()

        # Clear list
        for child in self._list.get_children():
            self._list.remove(child)

        # Populate list
        for quest in quest_set.get_quests(also_skippable=False):
            button = CharacterMissionButton(quest_set, quest)
            button.connect('clicked', self._quest_button_clicked_cb)
            self._list.add(button)
            button.show()

    def _quest_button_clicked_cb(self, button):
        quest_set = button.get_quest_set()
        new_quest = button.get_quest()
        easier_quest = quest_set.get_easier_quest(new_quest)
        if easier_quest is not None:
            # @todo: Offer easier quest.
            logger.info('Quest %s is too difficult, try quest %s', new_quest, easier_quest)

        self.clear_messages()
        self._app_window.run_quest(new_quest)


@Gtk.Template.from_resource('/com/endlessm/Clubhouse/clubhouse-view.ui')
class ClubhouseView(Gtk.EventBox):

    __gtype_name__ = 'ClubhouseView'

    _hack_switch = Gtk.Template.Child()
    _overlay_msg_box = Gtk.Template.Child()
    _main_characters_box = Gtk.Template.Child()
    _main_box = Gtk.Template.Child()

    class _QuestScheduleInfo:
        def __init__(self, quest, confirm_before, timeout, handler_id):
            self.quest = quest
            self.confirm_before = confirm_before
            self.timeout = timeout
            self.handler_id = handler_id

    def __init__(self, app_window):
        super().__init__(visible=True)

        self.scale = 1
        self._height_offset = 0
        self._current_quest = None
        self._scheduled_quest_info = None
        self._proposing_quest = False
        self._delayed_message_handler = 0

        self._last_user_answer = 0

        self._app_window = app_window
        self._app_window.connect('key-press-event', self._key_press_event_cb)
        self._app_window.connect('notify::visible', self._on_window_visibility_changed)

        self._app = Gio.Application.get_default()

        self._message = Message()
        self._message.connect('closed', self._hide_message_overlay_cb)
        self._overlay_msg_box.add(self._message)
        self._reset_quest_actions()

        self._current_episode = None
        self._current_quest_notification = None

        self.add_tick_callback(AnimationSystem.step)

        Desktop.shell_settings_bind(Desktop.SETTINGS_HACK_MODE_KEY, self._hack_switch, 'active')

        self._gss = GameStateService()
        self._gss_hander_id = self._gss.connect('changed',
                                                lambda _gss: self._update_episode_if_needed())

    def sync_with_hack_mode(self):
        hack_mode_enabled = Desktop.get_hack_mode()

        if not hack_mode_enabled:
            self.stop_quest()
            self._overlay_msg_box.hide()

        # Style.
        style_context = self.get_style_context()
        style_context.add_class('transitionable-background')
        if hack_mode_enabled:
            style_context.add_class('clubhouse-view')
            style_context.remove_class('clubhouse-view-off')
        else:
            style_context.remove_class('clubhouse-view')
            style_context.add_class('clubhouse-view-off')

    def _on_window_visibility_changed(self, _window, _param):
        if not self._app_window.props.visible:
            self._overlay_msg_box.hide()

    def _hide_message_overlay_cb(self, message):
        self._overlay_msg_box.hide()

    @Gtk.Template.Callback()
    def _on_button_press_event_cb(self, main_box, event):
        if event.get_button().button == 1:
            self._message.close()
            return True

        return False

    def set_scale(self, scale, offset=0):
        self.scale = scale
        self._height_offset = offset

        # Update children
        for child in self._main_characters_box.get_children():
            if isinstance(child, QuestSetButton):
                child.reload(self.scale)

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
        x, y = button.position
        self._main_characters_box.move(button, x, y + self._height_offset)

    def add_quest_set(self, quest_set):
        button = QuestSetButton(quest_set, self.scale)
        quest_set.connect('notify::highlighted', self._on_quest_set_highlighted_changed)
        button.connect('clicked', self._button_clicked_cb)

        x, y = button.position
        self._main_characters_box.put(button, x, y + self._height_offset)

        button.connect('notify::position', self._on_button_position_changed)

    def _on_quest_set_highlighted_changed(self, quest_set, _param):
        if self._app_window.is_visible():
            return

        self._app.send_suggest_open(libquest.Registry.has_quest_sets_highlighted())

    def _show_quest_continue_confirmation(self):
        if self._current_quest is None:
            return

        msg, continue_label, stop_label = self._current_quest.get_continue_info()
        self._message.update({
            'text': msg,
            'choices': [(continue_label, self._continue_quest, self._current_quest),
                        (stop_label, self._stop_quest_from_message, self._current_quest)],
            'character_id': self._current_quest.get_main_character()
        })

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
        # Hide the message here because it may be showing from another quest set
        self._overlay_msg_box.hide()

    def _button_clicked_cb(self, button):
        self.ask_character(button.get_quest_set())

    def ask_character(self, quest_set):
        self._message.reset()

        if isinstance(quest_set, libquest.CharacterMission):
            # @todo: ask user if we want to move to the other page?
            self._app_window.character.show_mission_list(quest_set)
            self._app_window.set_page('CHARACTER')
            return

        # @todo: Remove old behavior below.

        # If a quest from this quest_set is already running, then just hide the window so the
        # user focuses on the Shell's quest dialog
        if self._current_quest:
            if self._current_quest.available and self._current_quest in quest_set.get_quests() and \
               not self._current_quest.stopping:
                self._show_quest_continue_confirmation()
                return

        new_quest = quest_set.get_next_quest()

        self._stop_quest_proposal()

        if new_quest is None:
            character_id = quest_set.get_character()
            character = Character.get_or_create(character_id)
            character.mood = None

            msg_text = quest_set.get_empty_message()

            # If a QuestSet has overridden the empty message to be None, then don't
            # show anything
            if msg_text is None:
                self._message.set_character(character_id)
                return
            else:
                self._message.update({
                    'text': msg_text,
                    'choices': [('Ok', self._message.close)],
                    'character_id': character_id
                })
        else:
            character_id = new_quest.get_main_character()
            character = Character.get_or_create(character_id)
            character.mood = new_quest.proposal_mood
            self._message.update({
                'text': new_quest.proposal_message,
                'choices': [(new_quest.accept_label, self._accept_quest_message, quest_set,
                             new_quest),
                            (new_quest.reject_label, self._message.close)],
                'character_id': character_id,
                'sound_fx': new_quest.proposal_sound
            })

        self._overlay_msg_box.show_all()

    def continue_playing(self):
        # If there is a running quest, we ask the quest's character whether to continue/stop it.
        if self._current_quest:
            quest_set = libquest.Registry.get_character_mission_for_quest(self._current_quest)
            if self._current_quest.available and quest_set is not None:
                self.ask_character(quest_set)
                return

        # Ask the first character that is active what to do (start/continue a quest, etc.).
        for quest_set in libquest.Registry.get_quest_sets():
            if quest_set.is_active():
                self.ask_character(quest_set)

    def _stop_quest_proposal(self):
        if self._proposing_quest:
            self._shell_close_popup_message()
            self._proposing_quest = False

    def _accept_quest_message(self, _quest_set, new_quest):
        self._message.hide()
        self._overlay_msg_box.hide()
        logger.info('Start quest {}'.format(new_quest))
        self._app_window.run_quest(new_quest)

    def connect_quest(self, quest):
        # Don't update the episode if we're running a quest; this is so we avoid reloading the
        # Clubhouse while running a quest if it changes the episode.
        self._gss.handler_block(self._gss_hander_id)

        quest.connect('message', self._quest_message_cb)
        quest.connect('dismiss-message', self._quest_dismiss_message_cb)
        quest.connect('schedule-quest', self._quest_scheduled_cb)
        quest.connect('item-given', self._quest_item_given_cb)

    def disconnect_quest(self, quest):
        self._gss.handler_unblock(self._gss_hander_id)
        quest.disconnect_by_func(self._quest_message_cb)
        quest.disconnect_by_func(self._quest_dismiss_message_cb)
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

    def _quest_message_cb(self, quest, message_info):
        logger.debug('Message %s: %s character_id=%s mood=%s choices=[%s]',
                     message_info['id'], message_info['text'],
                     message_info['character_id'], message_info['character_mood'],
                     '|'.join([answer for answer, _cb, *_args in message_info['choices']]))

        character = Character.get_or_create(message_info['character_id'])
        character.mood = message_info['character_mood']

        if message_info['type'] == libquest.Quest.MessageType.POPUP:
            self._reset_quest_actions()

            for answer in message_info['choices']:
                self._add_quest_action(answer)

            self._shell_popup_message(message_info['text'], character,
                                      message_info['sound_fx'], message_info['sound_bg'])

        elif message_info['type'] == libquest.Quest.MessageType.NARRATIVE:
            character = Character.get_or_create(message_info['character_id'])
            character.mood = message_info['character_mood']
            msg = self._app_window.character.add_message(message_info)
            msg.show()

    def _quest_dismiss_message_cb(self, quest, narrative=False):
        if not narrative:
            self._shell_close_popup_message()
        else:
            self._message.close()
            self._app_window.character.clear_messages()

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
        quest_set = libquest.Registry.get_character_mission_for_quest(quest)

        self._reset_quest_actions()

        for answer in [(quest.accept_label, self._accept_quest_message, quest_set, quest),
                       (quest.reject_label, self._stop_quest_proposal)]:
            self._add_quest_action(answer)

        self._proposing_quest = True

        character = Character.get_or_create(quest.get_main_character())
        character.mood = quest.proposal_mood
        self._shell_popup_message(quest.proposal_message, character, quest.proposal_sound)

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

    def _shell_popup_message(self, text, character, sfx_sound, bg_sound=None):
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

        # We close the popup once we get a response from the user, otherwise the dialog would just
        # keep getting displayed until closed or replaced from elsewhere.
        self._shell_close_popup_message()

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
        for quest_set in libquest.Registry.get_character_missions():
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
                                use_markup=True,
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


class PathwaysView(Gtk.ListBox):
    def __init__(self, app_window):
        super().__init__(visible=True)

        self._app_window = app_window
        self.get_style_context().add_class('pathways-view')

    def load_episode(self):
        for pathway in libquest.Registry.get_pathways():
            self._add_pathway(pathway)

    def _quest_button_clicked_cb(self, button):
        new_quest = button.get_quest()
        self._app_window.run_quest(new_quest)

    def _add_pathway(self, pathway):
        vbox = Gtk.Box(halign=Gtk.Align.FILL,
                       orientation=Gtk.Orientation.VERTICAL)

        label = Gtk.Label(wrap=True,
                          hexpand=False,
                          halign=Gtk.Align.CENTER,
                          justify=Gtk.Justification.CENTER,
                          label=pathway.get_name())

        vbox.add(label)
        label.show()

        for quest in pathway.get_quests(also_skippable=False):
            button = QuestButton(quest)
            button.connect('clicked', self._quest_button_clicked_cb)
            vbox.add(button)
            button.show()

        self.add(vbox)
        vbox.show()


class InventoryView(Gtk.EventBox):

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
        self.get_style_context().add_class('inventory-view')

        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/inventory-view.ui')

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


class EpisodeRow(Gtk.ListBoxRow):

    __gsignals__ = {
        'badge-clicked': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
    }

    BADGE_INNER_MARGIN = 25

    def __init__(self, episode, badges_box):
        super().__init__(selectable=(episode.is_complete() or episode.is_current))
        self._episode = episode

        self._badges_box = badges_box
        self._badge = None
        self._badge_position_handler = 0

        self._poster = None

        self._setup_ui()

    def _setup_ui(self):
        self.get_style_context().add_class('episode-row')
        if not self._episode.is_complete() and not self._episode.is_current:
            self.get_style_context().add_class('episode-row-locked')

        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/episode-row.ui')

        self._expand_button = builder.get_object('episode_row_expand_button')
        episode_name_label = builder.get_object('episode_row_name_label')
        episode_number_label = builder.get_object('episode_row_number_label')
        episode_comingsoon_label = builder.get_object('episode_row_comingsoon_label')

        episode_number_text = 'Episode {}'.format(self._episode.number)

        height = 104
        if self._episode.percentage_complete != 100 and not self._episode.is_current:
            height = 64
            episode_name_label.set_label(episode_number_text)
            episode_number_label.hide()
            self._expand_button.set_sensitive(False)
            if not self._episode.is_available:
                episode_comingsoon_label.set_visible(True)
        else:
            episode_name_label.set_label(self._episode.name)
            episode_number_label.set_label(episode_number_text)
            episode_number_label.show()

            self._description_label = builder.get_object('episode_row_description_label')
            self._description_label.set_markup(self._episode.description)

            self._revealer = builder.get_object('episode_row_revealer')

            self._expand_button.connect('clicked', lambda _button: self._toggle_selection())

        self.connect('state-flags-changed', self._on_state_changed)

        self._expand_button.set_size_request(-1, height)

        self.add(builder.get_object('episode_row_box'))

        self._setup_badge()

    def _on_state_changed(self, _row, previous_flags):
        previously_selected = previous_flags & Gtk.StateFlags.SELECTED
        currently_selected = self.get_state_flags() & Gtk.StateFlags.SELECTED

        # Only reveal the description if the row got selected or unselected
        if previously_selected ^ currently_selected:
            self._revealer.set_reveal_child(currently_selected != 0)

    def _toggle_selection(self):
        list_box = self.get_parent()
        if list_box is None:
            return

        if self.is_selected():
            list_box.unselect_row(self)
        else:
            list_box.select_row(self)

    def _setup_badge(self):
        if not self._episode.is_available:
            return

        self._badge = BadgeButton(self._episode)
        self._badges_box.put(self._badge, 0, 0)
        self._badge.show()

        self._update_badge_position()

        if self._badge_position_handler == 0:
            self._badge_position_handler = \
                self._expand_button.connect('size-allocate',
                                            lambda _widget, _alloc: self._update_badge_position())

            # Update the badges position when the badges box is realized to make sure we place the
            # badges when both the rows' button + the badges box have valid dimensions.
            self._badges_box.connect_after('realize',
                                           lambda _widget: self._update_badge_position())

        self._badge.connect('clicked', self._badge_clicked_cb)

    def _update_badge_position(self):
        if not self.get_realized() or not self._badges_box.get_realized():
            return

        # We only use the button's allocation for getting the vertical position on which to set
        # the badge (and not the width), otherwise the badges would move when the scrollbar
        # appears (because the buttons are shortened horizontally when that happens).
        height = self._expand_button.get_allocation().height
        width = self.get_parent().get_allocation().width

        pos_x, pos_y = self._expand_button.translate_coordinates(self._badges_box,
                                                                 width,
                                                                 height / 2.0)

        # Place the badge horizontally as if aligned to the right.
        pos_x -= self._badge.WIDTH
        # Place the badge vertically using the middle-point as the anchor.
        pos_y -= self._badge.HEIGHT / 2.0

        # Pull the odd-numbered (1-based indexing) episodes further to the left (to accomplish
        # the zig-zag placement).
        if self._episode.number % 2 != 0:
            pos_x -= self._badge.WIDTH / 2.0 - self.BADGE_INNER_MARGIN

        self._badges_box.move(self._badge, pos_x, pos_y)

    def get_badge(self):
        return self._badge

    def get_episode(self):
        return self._episode

    def do_destroy(self):
        self.get_badge().destroy()

    def _badge_clicked_cb(self, _badge):
        self.emit('badge-clicked')

    def show_poster(self):
        if self._poster is None:
            self._poster = PosterWindow(self._episode)
        self._poster.show()
        self._poster.present()


class EpisodesView(Gtk.EventBox):

    __gsignals__ = {
        'play-episode': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
    }

    _COMPLETED = 'completed'

    def __init__(self, app_window):
        super().__init__(visible=True)

        self._episodes_db = utils.EpisodesDB()

        self._app_window = app_window
        self._current_page = None
        self._current_episode = None
        self._episodes = {}

        self._setup_ui()
        self._update_episode_badges()

        GameStateService().connect('changed', lambda _gss: self._update_episode_badges())

    def _setup_ui(self):
        self.get_style_context().add_class('episodes-view')

        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/episodes-view.ui')

        self._badges_box = builder.get_object('badges_box')
        self._badges_box.show_all()
        episodes_overlay = builder.get_object('episodes_overlay')
        episodes_overlay.set_overlay_pass_through(self._badges_box, True)
        self._list_box = builder.get_object('episodes_list_box')

        self.add(builder.get_object('episodes_scrolled_window'))

        self.reload()

    def reload(self):
        # Clear the episodes list.
        self._episodes = {}
        for row in self._list_box.get_children():
            row.destroy()

        available_episodes = set(libquest.Registry.get_available_episodes())
        loaded_episode = libquest.Registry.get_loaded_episode_name()
        episode = self._episodes_db.get_episode(loaded_episode)

        completed_episodes = self._episodes_db.get_previous_episodes(episode.id)
        for episode in self._episodes_db.get_episodes_in_season(episode.season):
            if episode in completed_episodes:
                episode.percentage_complete = 100
            elif episode.id == loaded_episode:
                episode.is_current = True
            else:
                episode.percentage_complete = 0

            if episode.id in available_episodes:
                episode.is_available = True

            row = EpisodeRow(episode, self._badges_box)
            row.connect('badge-clicked', self._episode_badge_clicked_cb)
            self._list_box.add(row)
            row.show()

            # @todo: Remove the need for an episodes dictionary (it can be done by keeping
            # the current episode object accessible).
            self._episodes[episode.id] = row

            # If this is the row for the current episode, we select it, so it shows the
            # description by default.
            if episode.is_current:
                self._list_box.select_row(row)

        self.update_current_episode()

    def _episode_badge_clicked_cb(self, episode_row):
        episode = episode_row.get_episode()
        if episode.is_complete():
            episode_row.show_poster()
            return

        if episode.is_current:
            self.emit('play-episode')

    def _get_current_episode(self):
        loaded_episode = libquest.Registry.get_loaded_episode_name()
        return self._episodes[loaded_episode].get_episode()

    def update_current_episode(self):
        episode = self._get_current_episode()
        episode.percentage_complete = libquest.Registry.get_current_episode_progress() * 100

        if episode.is_complete():
            self._shell_popup_episode_badge(episode.id)

    def _shell_popup_episode_badge(self, episode_id):
        notification = Gio.Notification()
        notification.set_body("You have a new badge! You can find it in the Episodes tab.")
        notification.set_title('')

        icon_path = os.path.join(config.EPISODES_DIR, 'badges', '{}.png'.format(episode_id))
        icon_file = Gio.File.new_for_path(icon_path)
        icon_bytes = icon_file.load_bytes(None)
        icon = Gio.BytesIcon.new(icon_bytes[0])

        notification.set_icon(icon)

        notification.add_button('Show me', 'app.episode-award-accept-answer(true)')

        Gio.Application.get_default().send_quest_item_notification(notification)

    def _update_episode_badges(self):
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
            self._episodes[episode_name].show_poster()

        # Only update the teaser-viewed info if there hasn't been an episode change.
        if is_same_episode:
            libquest.Registry.set_current_episode_teaser_viewed(True)


@Gtk.Template.from_resource('/com/endlessm/Clubhouse/clubhouse-window.ui')
class ClubhouseWindow(Gtk.ApplicationWindow):

    __gtype_name__ = 'ClubhouseWindow'
    _MAIN_PAGE_RESET_TIMEOUT = 60  # sec

    _headerbar = Gtk.Template.Child()
    _headerbar_box = Gtk.Template.Child()
    _stack = Gtk.Template.Child()
    _clubhouse_page = Gtk.Template.Child()
    _inventory_page = Gtk.Template.Child()
    _pathways_sw = Gtk.Template.Child()
    _user_label = Gtk.Template.Child()

    _pathways_button = Gtk.Template.Child()

    def __init__(self, app):
        super().__init__(application=app, title='Clubhouse')

        self._shell_settings = Gio.Settings('org.gnome.shell')

        self._page_reset_timeout = 0
        self._ambient_sound_uuid = None

        self.clubhouse = ClubhouseView(self)
        self.pathways = PathwaysView(self)
        self.inventory = InventoryView(self)
        self.character = CharacterView(self)

        self._clubhouse_page.pack_start(self.clubhouse, True, True, 0)
        self._inventory_page.pack_start(self.inventory, True, True, 0)
        self._pathways_sw.add(self.pathways)
        self._stack.add_named(self.character, 'CHARACTER')

        self.sync_with_hack_mode(init=True)
        Desktop.shell_settings_connect('changed::{}'.format(Desktop.SETTINGS_HACK_MODE_KEY),
                                       self._hack_mode_changed_cb)

        self._clubhouse_state = ClubhouseState()
        self._clubhouse_state.connect('notify::window-is-visible',
                                      self._on_clubhouse_window_visibility_changed_cb)

        self.update_user_info()
        self._on_screen_changed(self, None)
        self.connect('screen-changed', self._on_screen_changed)

    def _hack_mode_changed_cb(self, _settings, _key):
        self.sync_with_hack_mode()

    def sync_with_hack_mode(self, init=False):
        hack_mode_enabled = Desktop.get_hack_mode()

        if not init:
            Desktop.set_hack_background(hack_mode_enabled)
        Desktop.set_hack_cursor(hack_mode_enabled)
        self._pathways_button.props.sensitive = hack_mode_enabled

        # Style.
        ctx = self.get_titlebar().get_style_context()
        ctx.add_class('transitionable-background')
        if hack_mode_enabled:
            ctx.remove_class('CLUBHOUSE-off')
            ctx.add_class('CLUBHOUSE')
        else:
            ctx.remove_class('CLUBHOUSE')
            ctx.add_class('CLUBHOUSE-off')

        self.clubhouse.sync_with_hack_mode()

    def _update_window_size(self):
        BG_WIDTH = 1200
        BG_HEIGHT = 810

        screen_height = self.get_screen().get_height()

        # Remove small/big css classes
        context = self.get_style_context()
        context.remove_class('small')
        context.remove_class('big')

        # Add class depending on screen size
        if screen_height <= 720:
            context.add_class('small')
        elif screen_height >= 1080:
            context.add_class('big')

        # Clamp resolution to 75% of 720p-1080p
        height = max(720, min(screen_height, 1080)) * 0.75

        headerbar_height = self._headerbar.get_allocated_height()

        # Set main stack size
        self._stack.set_size_request(height * BG_WIDTH / BG_HEIGHT,
                                     height - headerbar_height)

        scale = height / BG_HEIGHT
        self.clubhouse.set_scale(scale, -headerbar_height)
        self.character.set_scale(scale)

    @Gtk.Template.Callback()
    def _on_headerbar_size_allocated(self, titlebar, allocation):
        self._update_window_size()

    def _on_screen_size_changed(self, screen):
        self._update_window_size()

    def _on_screen_changed(self, widget, previous_screen):
        if previous_screen is not None:
            previous_screen.disconnect_by_func(self._on_screen_size_changed)

        screen = self.get_screen()
        self._on_screen_size_changed(screen)
        screen.connect('size-changed', self._on_screen_size_changed)

    def _on_clubhouse_window_visibility_changed_cb(self, state, _param):
        if state.window_is_visible:
            self.show()
        else:
            self.hide()

    def update_user_info(self):
        self._user_label.set_label(GLib.get_real_name())
        # @todo: update self._user_image

    def continue_playing(self):
        self.clubhouse.continue_playing()
        # Select main page so the user can see whether a character is now offering a quest.
        self._stack.set_visible_child(self._clubhouse_page)

    @Gtk.Template.Callback()
    def _on_delete(self, widget, _event):
        widget.hide()
        return True

    def set_page(self, page_name):
        current_page = self._stack.get_visible_child_name()
        new_page = page_name.upper()

        if current_page == new_page:
            return

        # Set a different headerbar css class depending on the page
        ctx = self._headerbar.get_style_context()
        ctx.remove_class(current_page)

        # Avoid transition between other tabs with the Clubhouse view tab.
        ctx.remove_class('{}-off'.format(current_page))
        ctx.remove_class('transitionable-background')
        style_class = new_page
        if self._stack.get_child_by_name(new_page) == self._clubhouse_page:
            hack_mode_enabled = Desktop.get_hack_mode()
            if not hack_mode_enabled:
                style_class = '{}-off'.format(new_page)

        ctx.add_class(style_class)

        page = self._stack.get_child_by_name(new_page)

        if hasattr(page, 'header_box') and page.header_box is not None:
            self._headerbar.set_custom_title(page.header_box)
        else:
            self._headerbar.set_custom_title(self._headerbar_box)

        # Switch page
        self._stack.set_visible_child(page)

    def _select_main_page_on_timeout(self):
        self._stack.set_visible_child(self._clubhouse_page)
        self._page_reset_timeout = 0

        return GLib.SOURCE_REMOVE

    def _stop_page_reset_timeout(self):
        if self._page_reset_timeout > 0:
            GLib.source_remove(self._page_reset_timeout)
            self._page_reset_timeout = 0

    def _reset_selected_page_on_timeout(self):
        self._stop_page_reset_timeout()

        if self._stack.get_visible_child() == self._clubhouse_page:
            return

        self._page_reset_timeout = GLib.timeout_add_seconds(self._MAIN_PAGE_RESET_TIMEOUT,
                                                            self._select_main_page_on_timeout)

    @Gtk.Template.Callback()
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

    def run_quest(self, quest):
        logger.info('Start quest {}'.format(quest))
        self.clubhouse.run_quest(quest)


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

        self.add_main_option('list-quests', ord('q'), GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'List existing quest sets and quests', None)
        self.add_main_option('list-episodes', 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'List available episodes', None)
        self.add_main_option('get-episode', 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'Print the current episode', None)
        self.add_main_option('set-episode', 0, GLib.OptionFlags.NONE, GLib.OptionArg.STRING,
                             'Switch to this episode, marking it as not complete', 'EPISODE_NAME')
        self.add_main_option('set-quest', 0, GLib.OptionFlags.NONE, GLib.OptionArg.STRING,
                             'Make a quest available to be started. This completes all the '
                             'quests before the given one, making it available.',
                             '[EPISODE_NAME.]QUEST_NAME')
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
        if not self._run_episode_autorun_quest_if_needed():
            self.show(Gdk.CURRENT_TIME)

    def _run_episode_autorun_quest_if_needed(self):
        autorun_quest = libquest.Registry.get_autorun_quest()
        if autorun_quest is None:
            return

        quest = libquest.Registry.get_quest_by_name(autorun_quest)
        if not quest.complete:
            # Run the quest in the app's main instance
            self.activate_action('run-quest', GLib.Variant('(sb)', (autorun_quest, True)))
            return True

        return False

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

        if options.contains('set-quest'):
            episode_value = options.lookup_value('set-quest', GLib.VariantType('s'))
            full_name = episode_value.get_string()

            # The quest can be set with the episode name prefix, e.g. episode1.Fizzics2 .
            full_name_split = full_name.split('.', 1)

            if len(full_name_split) == 1:
                episode_name = None
                quest_id = full_name_split[0]
            else:
                episode_name, quest_id = full_name_split

            self._setup_quest(episode_name, quest_id)

            return 0

        if options.contains('reset'):
            self.activate_action('quit', None)
            return self._reset()

        if options.contains('debug'):
            self.activate_action('debug-mode', GLib.Variant('b', True))
            return 0

        if options.contains('quit'):
            self.activate_action('quit', None)
            return 0

        return -1

    def do_startup(self):
        Gtk.Application.do_startup(self)

        self._ensure_registry_loaded()
        self._ensure_suggesting_open()
        self._init_style()

        simple_actions = [('debug-mode', self._debug_mode_action_cb, GLib.VariantType.new('b')),
                          ('item-accept-answer', self._item_accept_action_cb,
                           GLib.VariantType.new('b'), 'inventory'),
                          ('episode-award-accept-answer', self._item_accept_action_cb,
                           GLib.VariantType.new('b'), 'episodes'),
                          ('quest-debug-skip', self._quest_debug_skip, None),
                          ('quest-user-answer', self._quest_user_answer, GLib.VariantType.new('s')),
                          ('quest-view-close', self._quest_view_close_action_cb, None),
                          ('quit', self._quit_action_cb, None),
                          ('close', self._close_action_cb, None),
                          ('run-quest', self._run_quest_action_cb, GLib.VariantType.new('(sb)')),
                          ('show-page', self._show_page_action_cb, GLib.VariantType.new('s')),
                          ('stop-quest', self._stop_quest, None),
                          ]

        for name, callback, variant_type, *callback_args in simple_actions:
            action = Gio.SimpleAction.new(name, variant_type)
            action.connect('activate', callback, *callback_args)
            self.add_action(action)

    def _ensure_registry_loaded(self):
        if not self._registry_loaded:
            libquest.Registry.load_current_episode()
            self._registry_loaded = True

    def _ensure_suggesting_open(self):
        quest_sets = libquest.Registry.get_character_missions()
        for quest_set in quest_sets:
            if quest_set.highlighted:
                self.send_suggest_open(True)
                break

    def _load_episode(self):
        # @todo: Move staff from clubhouse_page.load_episode() here
        self._window.clubhouse.load_episode()
        self._window.pathways.load_episode()

    def _ensure_window(self):
        if self._window:
            return

        self._window = ClubhouseWindow(self)
        self._window.connect('notify::visible', self._visibility_notify_cb)
        self._window.clubhouse.connect('notify::running-quest',
                                       self._running_quest_notify_cb)

        self._load_episode()

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
            self._window.clubhouse.stop_quest()
        self.close_quest_msg_notification()

    def _item_accept_action_cb(self, action, arg_variant, page_to_select):
        Sound.play('quests/key-confirm')
        show_inventory = arg_variant.unpack()
        if show_inventory and self._window:
            self._window.set_page(page_to_select)
            self._show_and_focus_window()

    def _debug_mode_action_cb(self, action, arg_variant):
        # Add debugging information in the Application UI:
        self._debug_mode = arg_variant.unpack()
        self._ensure_window()

        # Also set the logging level:
        logger.setLevel(logging.DEBUG)

    def _quest_user_answer(self, action, action_id):
        if self._window:
            self._window.clubhouse.quest_action(action_id.unpack())

    def _quest_view_close_action_cb(self, _action, _action_id):
        logger.debug('Shell quest view closed')
        if self._window:
            self._window.clubhouse.set_quest_to_background()

    def _quest_debug_skip(self, action, action_id):
        if self._window:
            self._window.clubhouse.quest_debug_skip()

    def _run_quest_by_name(self, quest_name):
        self._ensure_window()
        self._window.clubhouse.run_quest_by_name(quest_name)

    def _run_quest_action_cb(self, action, arg_variant):
        quest_name, _obsolete = arg_variant.unpack()
        self._run_quest_by_name(quest_name)

    def _quit_action_cb(self, action, arg_variant):
        self._stop_quest()

        if self._window:
            self._window.destroy()
            self._window = None

        self.quit()

    def _close_action_cb(self, action, arg_variant):
        if self._window:
            self._window.hide()

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

    def _running_quest_notify_cb(self, _clubhouse, _pspec):
        changed_props = {'RunningQuest': GLib.Variant('s', self._get_running_quest_name())}
        self._emit_dbus_props_changed(changed_props)

    def _get_running_quest_name(self):
        if self._window is not None:
            quest = self._window.clubhouse.props.running_quest
            if quest is not None:
                return quest.get_id()
        return ''

    # D-Bus implementation
    def show(self, timestamp):
        if not self._run_episode_autorun_quest_if_needed():
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

    def _setup_quest(self, episode_name, quest_id):
        # Only load the episode if it's not already loaded.
        if episode_name is not None:
            available_episodes = libquest.Registry.get_available_episodes()
            if episode_name not in available_episodes:
                logger.error('Episode %s is not available.', episode_name)
                return 1
        else:
            episode_name = libquest.Registry.get_loaded_episode_name()

        GameStateService().reset()
        libquest.Registry.set_current_episode(episode_name, force=True)
        libquest.Registry.load_current_episode()

        quests = libquest.Registry.get_current_quests()

        print('Setting up {} as available'.format(quest_id))

        # Reset all quests as not completed so we then only get the desired quest's dependencies
        # as completed.
        for quest in quests.values():
            quest.complete = False
            quest.save_conf()

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
