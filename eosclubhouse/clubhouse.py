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
gi.require_version('EosMetrics', '0')
gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
gi.require_version('Json', '1.0')
import functools
import logging
import os
import re
import subprocess
import sys
import time
import datetime

from collections import OrderedDict
from gi.repository import EosMetrics, Gdk, GdkPixbuf, Gio, GLib, Gtk, GObject, \
    Json, Pango
from eosclubhouse import config, logger, libquest, utils
from eosclubhouse.achievements import AchievementsDB
from eosclubhouse.system import Desktop, GameStateService, OldGameStateService, \
    Sound, SoundItem, UserAccount
from eosclubhouse.utils import ClubhouseState, Performance, SimpleMarkupParser, \
    get_alternative_quests_dir
from eosclubhouse.animation import Animation, AnimationImage, AnimationSystem, Animator, \
    Direction, get_character_animation_dirs

from eosclubhouse.widgets import FixedLayerGroup


# Metrics event ids
CLUBHOUSE_SET_PAGE_EVENT = '2c765b36-a4c9-40ee-b313-dc73c4fa1f0d'
CLUBHOUSE_PATHWAY_ENTER_EVENT = '600c1cae-b391-4cb4-9930-ea284792fdfb'
HACK_MODE_EVENT = '7587784b-c3ed-4d74-b0fa-1023033698c0'


CLUBHOUSE_NAME = 'com.hack_computer.Clubhouse'
CLUBHOUSE_PATH = '/com/hack_computer/Clubhouse'
CLUBHOUSE_IFACE = CLUBHOUSE_NAME

ClubhouseIface = ('<node>'
                  '<interface name="com.hack_computer.Clubhouse">'
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
                  '<method name="migrationQuest">'
                  '</method>'
                  '<property name="Visible" type="b" access="read"/>'
                  '<property name="RunningQuest" type="s" access="read"/>'
                  '<property name="SuggestingOpen" type="b" access="read"/>'
                  '</interface>'
                  '</node>')

# Load Resources
resource = Gio.resource_load(os.path.join(config.DATA_DIR, 'eos-clubhouse.gresource'))
Gio.Resource._register(resource)

CharacterInfo = {
    'estelle': {
        'position': (610, 144),
        'username': 'lightspeedgal',
        'pathway': 'art',
        'pathway_title': 'Art'
    },
    'ada': {
        'position': (204, 182),
        'username': 'countesslovelace',
        'pathway': 'games',
        'pathway_title': 'Games'
    },
    'saniel': {
        'position': (892, 570),
        'username': 'srowe1822',
        'pathway': 'operatingsystem',
        'pathway_title': 'Operating Systems'
    },
    'faber': {
        'position': (518, 511),
        'username': 'fabersapiens',
        'pathway': 'maker',
        'pathway_title': 'Maker'
    },
    'riley': {
        'position': (298, 551),
        'username': '_getriled',
        'pathway': 'web',
        'pathway_title': 'Web'
    },
    'felix': {
        'position': None,
        'username': 'UNDEFINED_USER',
        'pathway': None,
        'pathway_title': None
    },
    'metatron': {
        'position': None,
        'username': 'Endless',
        'pathway': None,
        'pathway_title': None
    }
}


class Character(GObject.GObject):
    _characters = {}
    DEFAULT_MOOD = 'talk'
    DEFAULT_BODY_ANIMATION = 'idle'
    HIGHLIGHTED_ANIMATION = 'hi'
    LIGHTS_OFF_ANIMATION = 'idle-off'

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
        body_path = os.path.join(self._id, 'fullbody')
        self._body_image = AnimationImage(body_path)

        if id_ in CharacterInfo:
            info = CharacterInfo[id_]
            self._position = info['position']
            self.username = info['username']
            self.pathway = info['pathway']
            self.pathway_title = info['pathway_title']
        else:
            self._position = None
            self.username = None
            self.pathway = None
            self.pathway_title = None

    def _get_id(self):
        return self._id

    def _get_name(self):
        return self.id.capitalize()

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
        self._body_image.load(scale)
        self._body_image.play(self.DEFAULT_BODY_ANIMATION)

    def get_position(self):
        return self._position

    id = property(_get_id)
    name = property(_get_name)
    mood = GObject.Property(_get_mood, _set_mood, type=str)
    body_animation = GObject.Property(_get_body_animation, _set_body_animation, type=str)


class MessageButton(Gtk.Button):

    __gtype_name__ = 'MessageButton'

    ICONS_FOR_EMOJI = {
        '❯': ':icon:next:',
        '❮': ':icon:previous:',
        '👍': ':icon:thumbsup:',
        '👎': ':icon:thumbsdown:'
    }
    DEFAULT_ICON_WITH_LABEL_SIZE = 15
    DEFAULT_ICON_WITHOUT_LABEL_SIZE = 24

    def __init__(self, label, click_cb, *user_data):
        super().__init__()

        self._setup_ui(label)
        self.connect('clicked', self._clicked_cb, click_cb, *user_data)

    def _setup_ui(self, label):
        icon_name, label = self._parse_from_label(label)

        if icon_name:
            image = Gtk.Image(valign=Gtk.Align.CENTER, icon_name=icon_name)
            self.set_image(image)
            self.set_property('always-show-image', True)

        ctx = self.get_style_context()
        if self.props.image:
            if label:
                self.props.image.props.pixel_size = self.DEFAULT_ICON_WITH_LABEL_SIZE
            else:
                self.props.image.props.pixel_size = self.DEFAULT_ICON_WITHOUT_LABEL_SIZE
                ctx.add_class('icon-button')

        if label:
            self.props.label = label
            if self.props.image:
                label_widget = self.get_children()[0].get_children()[0].get_children()[1]
            else:
                label_widget = self.get_children()[0]
                ctx.add_class('text-button')
            label_widget.props.valign = Gtk.Align.CENTER

        self.props.valign = Gtk.Align.CENTER
        self.props.can_focus = False

    def _parse_from_label(self, label):
        # Backward compatibility.
        # @todo: Remove when quests implement the new :icon:icon-name: format.
        if label in self.ICONS_FOR_EMOJI:
            label = self.ICONS_FOR_EMOJI[label]

        tokens = re.split(r'(^\:icon:.*\:)', label)[1:]
        specifies_icon = bool(tokens)

        icon_name = None
        if specifies_icon:
            icon_name = 'clubhouse-{}'.format(tokens[0].split(':icon:')[1][:-1])
            label = tokens[1]

        return icon_name, label

    def _clicked_cb(self, button, caller_cb, *user_data):
        caller_cb(*user_data)


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/message.ui')
class Message(Gtk.Box):
    # Provided animation assets should not have a height that exceeds this standard height.
    CHARACTER_IMAGE_STANDARD_HEIGHT = 193

    __gtype_name__ = 'Message'

    _label = Gtk.Template.Child()
    _character_image = Gtk.Template.Child()
    _button_box = Gtk.Template.Child()

    OPEN_DIALOG_SOUND = 'clubhouse/dialog/open'

    def __init__(self):
        super().__init__()
        self._character = None
        self._character_mood_change_handler = 0
        self._animator = Animator(self._character_image)
        self._character_image.props.pixel_size = self.CHARACTER_IMAGE_STANDARD_HEIGHT
        self.connect("show", lambda _: Sound.play('clubhouse/dialog/open'))

    def set_text(self, txt):
        self._label.set_markup(SimpleMarkupParser.parse(txt))

    def get_text(self):
        return self._label.get_label()

    def add_button(self, label, click_cb, *user_data):
        button = MessageButton(label, click_cb, *user_data)
        button.show()
        self._button_box.pack_start(button, False, False, 0)
        self.get_style_context().add_class('has-buttons')
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

    def display_character(self, display):
        self._character_image.props.visible = display
        if display:
            self.get_style_context().add_class('has-character')
        else:
            self.get_style_context().remove_class('has-character')

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


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/quest-set-info-tip.ui')
class QuestSetInfoTip(Gtk.Box):

    __gtype_name__ = 'QuestSetInfoTip'

    _box = Gtk.Template.Child()
    _image = Gtk.Template.Child()
    _charater_name_label = Gtk.Template.Child()
    _pathway_name_label = Gtk.Template.Child()

    def __init__(self, quest_set_button):
        super().__init__()
        self.quest_set_button = quest_set_button
        self._image.props.icon_name = self._get_icon_name()
        self._charater_name_label.props.label = self.quest_set_button._character.name
        self._pathway_name_label.props.label = self.quest_set_button._character.pathway_title

    def fade_in(self):
        ctx = self.get_style_context()
        ctx.add_class('visible')

    def fade_out(self):
        ctx = self.get_style_context()
        ctx.remove_class('visible')

    def set_pathway_label_visible(self, visible):
        self._pathway_label.props.visible = visible

    def get_natural_width(self):
        return self._box.get_preferred_width().natural_width

    def _get_icon_name(self):
        pathway = self.quest_set_button._character.pathway or 'unknown'
        return 'clubhouse-pathway-{}-symbolic'.format(pathway)


class CharacterButton(Gtk.Button):

    __gtype_name__ = 'CharacterButton'

    def __init__(self, quest_set, scale=1):
        super().__init__(halign=Gtk.Align.START,
                         relief=Gtk.ReliefStyle.NONE)

        self._quest_set = quest_set
        self._character = Character.get_or_create(self._quest_set.get_character())

        image = self._character.get_body_image()
        self.add(image)
        image.show()

        self.reload(scale)

        self._quest_set.connect('notify::highlighted',
                                lambda _quest_set, highlighted: self._set_highlighted(highlighted))
        self._set_highlighted(self._quest_set.highlighted)

        self._previous_body_animation = None
        self._on_hover = False

        clubhouse_state = ClubhouseState()
        clubhouse_state.connect('notify::characters-disabled',
                                self._on_characters_disabled_changed_cb)
        clubhouse_state.connect('notify::lights-on',
                                self._on_lights_changed_cb)

        self._update_sensitivity(clubhouse_state)
        self._update_character_animation()

        self.connect('clicked', self._on_button_clicked_cb)
        self.connect('enter', self._on_button_enter_cb)
        self.connect('leave', self._on_button_leave_cb)

        # The button should only be visible when the QuestSet is visible
        self._quest_set.bind_property('visible', self, 'visible',
                                      GObject.BindingFlags.BIDIRECTIONAL |
                                      GObject.BindingFlags.SYNC_CREATE)

    def reload(self, scale):
        self._scale = scale
        # This 0.80 scale is because the new background is bigger so we need to
        # scale characters a bit to make it looks correctly in the new
        # background and not too big. This scale is done instead of the scale
        # for all animations.
        self._character.load(scale * 0.80)
        self.notify('position')

    def get_quest_set(self):
        return self._quest_set

    def _get_position(self):
        anchor = (0, 0)
        position = (0, 0)

        # Get the anchor (if any) so we adapt the position to it.
        if self._character:
            position = self._character.get_position() or position
            animation_image = self._character.get_body_image()
            if animation_image is not None:
                anchor = animation_image.get_anchor()

        return ((position[0] - anchor[0]) * self._scale,
                (position[1] - anchor[1]) * self._scale)

    def _on_button_clicked_cb(self, _button):
        if self._quest_set.highlighted:
            self._quest_set.highlighted = False

    def _on_button_enter_cb(self, _button):
        self._on_hover = True
        self._update_character_animation()

    def _on_button_leave_cb(self, _button):
        self._on_hover = False
        self._update_character_animation()

    def _set_highlighted(self, highlighted):
        highlighted_style = 'highlighted'
        style_context = self.get_style_context()
        if highlighted:
            style_context.add_class(highlighted_style)
        else:
            style_context.remove_class(highlighted_style)

    def _on_characters_disabled_changed_cb(self, state, _param):
        self._update_sensitivity(state)

    def _on_lights_changed_cb(self, state, _param):
        self._update_sensitivity(state)
        self._update_character_animation()

    def _update_sensitivity(self, state):
        # characters-disabled takes precedence over lights-on:
        if state.characters_disabled:
            self.props.sensitive = False
        else:
            self.props.sensitive = state.lights_on

    def _update_character_animation(self):
        new_animation = None

        if not ClubhouseState().lights_on:
            new_animation = self._character.LIGHTS_OFF_ANIMATION
        elif self._quest_set.highlighted or self._on_hover:
            new_animation = self._character.HIGHLIGHTED_ANIMATION
        else:
            new_animation = self._character.DEFAULT_BODY_ANIMATION

        if new_animation is not None:
            self._previous_body_animation = self._character.body_animation
            self._character.body_animation = new_animation
            self.notify('position')

    def _get_character(self):
        return self._character

    character = property(_get_character)
    position = GObject.Property(_get_position, type=GObject.TYPE_PYOBJECT)


class MessageBox(Gtk.Fixed):
    MIN_MESSAGE_WIDTH = 320
    MIN_MESSAGE_WIDTH_RATIO = 0.95

    DEFAULT_ANIMATION_INTERVAL_MS = 20
    DEFAULT_ANIMATION_DURATION_MS = 400

    def __init__(self, app_window):
        super().__init__()
        self._app_window = app_window
        self._messages_in_scene = []

    def _animate_message(self, message, direction, end_position, done_action_cb=None, *args):
        if direction in (Direction.LEFT, Direction.RIGHT):
            axis_prop = 'x'
        else:
            axis_prop = 'y'

        start_position = self.child_get_property(message, axis_prop)
        distance = abs(end_position - start_position)
        speed_ms_per_px = distance / self.DEFAULT_ANIMATION_DURATION_MS
        delta = speed_ms_per_px * self.DEFAULT_ANIMATION_INTERVAL_MS
        if direction in (Direction.LEFT, Direction.UP):
            delta = -delta

        if direction in (Direction.LEFT, Direction.RIGHT):
            if done_action_cb != self.remove:
                message.props.opacity = 0.0

        fade_in = direction in (Direction.LEFT, Direction.RIGHT)
        GLib.timeout_add(self.DEFAULT_ANIMATION_INTERVAL_MS, self._move_message_cb, message,
                         start_position, end_position, distance, delta, direction, axis_prop,
                         fade_in, done_action_cb, *args)

    def _move_message_cb(self, message, start_position, end_position, distance, delta, direction,
                         axis_prop, fade_in, done_action_cb, *args):
        def _update_message_opacity(opacity=None):
            if not fade_in:
                return

            if opacity is not None:
                message.props.opacity = opacity
                return

            traveled_distance_ratio = abs(new_position - start_position) / distance
            if done_action_cb != self.remove:
                message.props.opacity = traveled_distance_ratio
            else:
                message.props.opacity = 1 - traveled_distance_ratio

        current_position = self.child_get_property(message, axis_prop)
        new_position = current_position + delta

        negative_directions = (Direction.LEFT, Direction.UP)
        positive_directions = (Direction.RIGHT, Direction.DOWN)

        if (direction in negative_directions and new_position <= end_position or
                direction in positive_directions and new_position >= end_position):

            self.child_set_property(message, axis_prop, end_position)
            if done_action_cb == self.remove:
                _update_message_opacity(0.0)
            else:
                _update_message_opacity(1.0)

            if done_action_cb is not None:
                done_action_cb(*args)
            return GLib.SOURCE_REMOVE

        self.child_set_property(message, axis_prop, new_position)
        _update_message_opacity()
        return True

    def clear_messages(self):
        # @todo: Cancel pending/delayed message additions.
        for message in self.get_children():
            self.remove(message)
        self._messages_in_scene = []
        self._app_window.character.update_character_image(idle=True)

    def _is_main_character_message(self, message_info):
        return message_info.get('character_id') == self._app_window.character._character.id

    def _guess_message_direction(self, message):
        if message.get_character().id == self._app_window.character._character.id:
            return Direction.RIGHT
        return Direction.LEFT

    def _build_message_from_info(self, message_info):
        msg = Message()
        msg.update(message_info)

        overlay_width = self._app_window.character.character_image.get_allocation().width
        msg.props.width_request = \
            min(overlay_width, max(self.MIN_MESSAGE_WIDTH,
                                   overlay_width * self.MIN_MESSAGE_WIDTH_RATIO))

        if self._is_main_character_message(message_info):
            msg.display_character(False)
            msg.props.halign = Gtk.Align.START
        else:
            msg.display_character(True)
        return msg

    def add_message(self, message_info):
        current_quest = self._app_window.clubhouse.running_quest
        if current_quest is None or current_quest.stopping:
            return

        message = self._build_message_from_info(message_info)
        direction = self._guess_message_direction(message)
        is_main_character_message = self._is_main_character_message(message_info)

        # Hide actions on old messages.
        for child_message in self.get_children():
            child_message.clear_buttons()

        messages_in_scene = [msg for msg in self._messages_in_scene]
        if len(messages_in_scene) == self.max_messages:
            self._withdraw_top_message()
            self._slide_messages_up_with_delay(messages_in_scene, message,
                                               self.DEFAULT_ANIMATION_DURATION_MS)
            self._add_message_with_delay(messages_in_scene, message, direction,
                                         is_main_character_message,
                                         self.DEFAULT_ANIMATION_DURATION_MS * 2)
        else:
            self._slide_messages_up(messages_in_scene, message)
            self._add_message_with_delay(messages_in_scene, message, direction,
                                         is_main_character_message,
                                         self.DEFAULT_ANIMATION_DURATION_MS)

    def _add_message(self, messages_in_scene, message, direction, is_main_character_message):
        initial_x_pos, initial_y_pos = self._get_next_initial_position(message, direction)
        final_x_pos = 0
        self.put(message, initial_x_pos, initial_y_pos)

        self._messages_in_scene.append(message)
        if not is_main_character_message:
            allocation = self._app_window.character.activities_sw.get_allocation()
            message_width = message.get_preferred_width().minimum_width
            final_x_pos = allocation.x - message_width
        self._animate_message(message, direction, final_x_pos)

        self._app_window.character.update_character_image(idle=not is_main_character_message)
        message.show()

    def _add_message_with_delay(self, messages_in_scene, message, direction,
                                is_main_character_message, duration_ms):
        GLib.timeout_add(duration_ms, self._add_message, messages_in_scene, message, direction,
                         is_main_character_message)

    def _get_next_initial_position(self, message, direction):
        assert direction in (Direction.LEFT, Direction.RIGHT)

        allocation = self.get_allocation()
        msg_height = self._get_message_height(message)

        y_pos = allocation.height - msg_height
        if direction == Direction.RIGHT:
            x_pos = -message.props.width_request
        else:
            x_pos = allocation.width / 2 - message.props.width_request / 2
        return x_pos, y_pos

    def _withdraw_top_message(self):
        message = self._messages_in_scene.pop(0)
        direction = self._guess_message_direction(message).get_opposite()
        assert direction in (Direction.LEFT, Direction.RIGHT)

        message_width = message.props.width_request
        if direction == Direction.LEFT:
            final_position = -message_width
        else:
            final_position = self.get_allocation().width / 2 - message_width / 2

        self._animate_message(message, direction, final_position, self.remove, message)

    def _slide_messages_up(self, messages_in_scene, new_message):
        new_message_height = self._get_message_height(new_message)
        if len(messages_in_scene) < self.max_messages:
            messages_to_slide = messages_in_scene
        else:
            messages_to_slide = messages_in_scene[1:]

        # @todo: Avoid these hardcoded values.
        fix_margin = -80
        for msg in messages_to_slide:
            current_y = self.child_get_property(msg, 'y')
            self._animate_message(msg, Direction.UP, current_y - new_message_height - fix_margin)

    def _slide_messages_up_with_delay(self, messages_in_scene, new_message, duration_ms):
        GLib.timeout_add(duration_ms, self._slide_messages_up, messages_in_scene, new_message)

    def _get_message_height(self, message):
        return message.get_preferred_height_for_width(message.props.width_request).natural_height

    max_messages = GObject.Property(default=2, type=int)


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/activity-card.ui')
class ActivityCard(Gtk.FlowBoxChild):

    __gtype_name__ = 'ActivityCard'

    _title = Gtk.Template.Child()
    _stack = Gtk.Template.Child()
    _complete_image = Gtk.Template.Child()

    _play_button = Gtk.Template.Child()

    _topbox = Gtk.Template.Child()
    _revealer = Gtk.Template.Child()
    _difficulty_box = Gtk.Template.Child()

    def __init__(self, clubhouse, quest_set, quest):
        super().__init__()

        self._clubhouse = clubhouse
        self._quest_set = quest_set
        self._button_press_time = 0
        self._quest = quest
        self._quest.connect('quest-started', self._on_quest_started)
        self._quest.connect('quest-finished', self._on_quest_finished)
        self._alternative_path = os.path.join(get_alternative_quests_dir(), 'cards')

        self._setup_background()

        # Populate info.
        self._populate_info()

        self._quest.connect('notify::complete', self._on_quest_complete_changed)
        self._set_complete()

        self._update_state()

    @Gtk.Template.Callback()
    def _on_enter_notify_event(self, widget, event):
        self.set_state_flags(Gtk.StateFlags.PRELIGHT, False)

    @Gtk.Template.Callback()
    def _on_leave_notify_event(self, widget, event):
        self.unset_state_flags(Gtk.StateFlags.PRELIGHT)

    @Gtk.Template.Callback()
    def _on_state_flags_changed(self, widget, flags):
        self._update_state()

    @Gtk.Template.Callback()
    def _on_play_button_clicked(self, button):
        easier_quest = self._quest_set.get_easier_quest(self._quest)
        self._clubhouse.try_running_quest(self._quest, easier_quest)

    @Gtk.Template.Callback()
    def _on_button_press_event(self, widget, event):
        # Consume button press event if card is selected
        if self.is_selected():
            # Save press button time
            self._button_press_time = event.time
            return True

        return False

    @Gtk.Template.Callback()
    def _on_button_release_event(self, widget, event):
        # Deselect card if its selected and press time was less than 400ms ago
        #
        # The default behavior of the multi press event controller used by
        # GtkFlowBox uses uses a 400ms timeout to know if the user wanted to
        # press it or not.
        #
        # Try to avoid the situation where the user press the button over the card
        # and release it somewhere else then press the button somewhere else and
        # release it over the card which without the timeout it will always
        # trigger the selection.
        #
        # We could keep track of enter and leave events but that will complicate
        # things even more
        #
        # @todo: this is the old way of handling events we should investigate
        # if it is possible to use a GtkGesture instead.
        if event.time - self._button_press_time < 400 and self.is_selected():
            self.get_parent().unselect_child(self)
            return True

        return False

    def _is_selected(self):
        return self.get_state_flags() & Gtk.StateFlags.SELECTED

    def _update_state(self):
        selected = self.is_selected()
        self._revealer.set_reveal_child(selected)
        self._difficulty_box.set_visible(not selected)

    def _setup_background(self):
        self._css_provider = Gtk.CssProvider()
        self._topbox.get_style_context().add_provider(self._css_provider,
                                                      Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)

        quest_id = self._quest.get_id().lower()
        character = self._quest_set.get_character()
        if character not in CharacterInfo:
            return

        info = CharacterInfo[character]
        pathway = info['pathway']

        img = '{}/{}.jpg'.format(self._alternative_path, quest_id)
        if not os.path.exists(img):
            img = '/app/share/eos-clubhouse/quests_files/cards/{}.jpg'.format(quest_id)
            if not os.path.exists(img):
                img = '/app/share/eos-clubhouse/quests_files/pathway-card-{}.svg'.format(pathway)

        css = "box {{ background-image: url('{}') }}".format(img).encode()
        self._css_provider.load_from_data(css)

    def _create_description_label(self, description):
        return Gtk.Label(visible=True,
                         label=description,
                         ellipsize=Pango.EllipsizeMode.END,
                         wrap=True,
                         xalign=0,
                         yalign=0,
                         lines=8)

    def _populate_info(self):
        self._title.props.label = self._quest.get_name()

        description = self._quest.get_label('QUEST_DESCRIPTION')
        if description is not None:
            label = self._create_description_label(description)
            subtitle = self._quest.get_label('QUEST_SUBTITLE')
            self._stack.add_titled(label, 'description', subtitle)

        tags = self._quest.get_label('QUEST_CONTENT_TAGS')
        if tags is not None:
            textview = Gtk.TextView(visible=True,
                                    name='tagsview',
                                    editable=False,
                                    sensitive=False,
                                    cursor_visible=False,
                                    wrap_mode=Gtk.WrapMode.WORD)
            textbuffer = textview.get_buffer()
            tags = tags.split(':')
            for tag in tags:
                anchor = textbuffer.create_child_anchor(textbuffer.get_end_iter())
                label = Gtk.Label(label=tag, visible=True)
                textview.add_child_at_anchor(label, anchor)
                textbuffer.insert(textbuffer.get_end_iter(), ' ', 1)

            title = self._quest.get_label('QUEST_CONTENT_TAGS_TITLE')
            self._stack.add_titled(textview, 'tags', title)

        # Set difficulty class
        self.get_style_context().add_class(self._quest.get_difficulty().name)

    def _update_play_button(self, running):
        if running:
            self._play_button.set_label('running...')
        elif self._quest.complete:
            self._play_button.set_label('play again')
            self._play_button.get_style_context().add_class('complete')
        else:
            self._play_button.get_style_context().remove_class('complete')
            self._play_button.set_label('play')

    def _on_quest_started(self, quest):
        self.props.sensitive = False
        self._update_play_button(True)

    def _on_quest_finished(self, quest):
        self.props.sensitive = True
        self._update_play_button(False)

    def _on_quest_complete_changed(self, _quest_set, _param):
        self._set_complete()

    def _set_complete(self):
        self._complete_image.props.visible = self._quest.complete
        self._update_play_button(False)

    def get_quest(self):
        return self._quest

    def get_quest_set(self):
        return self._quest_set


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/character-view.ui')
class CharacterView(Gtk.Grid):

    __gtype_name__ = 'CharacterView'

    header_box = Gtk.Template.Child()
    character_image = Gtk.Template.Child()
    activities_sw = Gtk.Template.Child()

    _list = Gtk.Template.Child()
    _view_overlay = Gtk.Template.Child()
    _character_button_label = Gtk.Template.Child()
    _clubhouse_button = Gtk.Template.Child()

    def __init__(self, app_window):
        super().__init__(visible=True)
        self._app_window = app_window

        self.message_box = MessageBox(app_window)
        self._view_overlay.add_overlay(self.message_box)
        self._view_overlay.set_overlay_pass_through(self.message_box, True)

        self._animator = Animator(self.character_image)
        self._character = None
        self._scale = 1

        self._clubhouse_state = ClubhouseState()
        self._clubhouse_state.connect('notify::nav-attract-state',
                                      self._on_clubhouse_nav_attract_state_changed_cb)
        self._clubhouse_state.connect('notify::characters-disabled',
                                      self._on_characters_disabled_changed_cb)

        self.message_box.show_all()

    def update_character_image(self, idle=False):
        if self._character is None:
            return

        animation_id = self._character.id + '/closeup-talk' + ('' if not idle else '-idle')
        if not self._animator.has_animation(animation_id) or \
           self._animator.get_animation_scale(animation_id) != self._scale:
            self._animator.load(self._character.get_moods_path(),
                                self._character.id,
                                self._scale)

        # @todo: play animation only when a dialog is added
        self._animator.play(animation_id)

    def set_scale(self, scale):
        self._scale = scale
        self.update_character_image(idle=True)

    def show_mission_list(self, quest_set):
        ctx = self._app_window.get_style_context()

        if self._character is not None:
            ctx.remove_class(self._character.id)

        # Get character
        self._character = Character.get_or_create(quest_set.get_character())

        ctx.add_class(self._character.id)

        # Set page title
        self._character_button_label.set_text(self._character.pathway_title)

        # Set character image
        self.update_character_image(idle=True)

        # Clear list
        for child in self._list.get_children():
            self._list.remove(child)

        # Populate list
        for quest in quest_set.get_quests(also_skippable=False):
            card = ActivityCard(self._app_window.clubhouse, quest_set, quest)
            self._list.add(card)
            card.show()

        # @todo: Scroll the first non completed quest.

    def _on_row_size_allocate(self, row, _rect):
        self._scroll_to_first_non_completed_quest()
        row.disconnect_by_func(self._on_row_size_allocate)

    def _scroll_to_mission_row_at_index(self, index, reference_row):
        vadjustment = self.activities_sw.props.vadjustment
        if index <= 0:
            vadjustment.props.value = 0
            return
        # @todo: Consider margins. Not margins are used now.
        reference_height = reference_row.get_allocation().height
        y = index * reference_height
        vadjustment.props.value = y

    def _get_first_non_completed_mission_index(self):
        for i, row in enumerate(self._list.get_children()):
            if not row.get_quest().complete:
                return i
        return -1

    def _scroll_to_first_non_completed_quest(self):
        index = self._get_first_non_completed_mission_index()
        reference_row = self._list.get_row_at_index(0)
        if reference_row:
            self._scroll_to_mission_row_at_index(index, reference_row)

    def _on_clubhouse_nav_attract_state_changed_cb(self, state, _param):
        if state.nav_attract_state == ClubhouseState.Page.CLUBHOUSE:
            self._clubhouse_button.get_style_context().add_class('nav-attract')
        else:
            self._clubhouse_button.get_style_context().remove_class('nav-attract')

    def _on_characters_disabled_changed_cb(self, state, _param):
        self._app_window.character.activities_sw.props.sensitive = not state.characters_disabled


class ClubhouseView(FixedLayerGroup):

    __gtype_name__ = 'ClubhouseView'

    MAIN_LAYER_NAME = 'main-layer'
    INFO_TIP_LAYER = 'infotip-layer'

    SYSTEM_CHARACTER_ID = 'daemon'
    SYSTEM_CHARACTER_MOOD = 'talk'

    class _QuestScheduleInfo:
        def __init__(self, quest, confirm_before, timeout, handler_id):
            self.quest = quest
            self.confirm_before = confirm_before
            self.timeout = timeout
            self.handler_id = handler_id

    def __init__(self, app_window):
        super().__init__()
        self.scale = 1
        self._current_quest = None
        self._scheduled_quest_info = None
        self._delayed_message_handler = 0

        self._last_user_answer = 0

        self._app_window = app_window

        self._app = Gio.Application.get_default()

        self._reset_quest_actions()

        self.current_episode = None
        self._current_quest_notification = None

        self.add_tick_callback(AnimationSystem.step)

        self._gss = GameStateService()
        self._gss_hander_id = self._gss.connect('changed',
                                                lambda _gss: self._update_episode_if_needed())

        registry = libquest.Registry.get_or_create()
        registry.connect('schedule-quest', self._quest_scheduled_cb)

        self._add_main_layer()
        self._add_info_tip_layer()

        self.show_all()

    def get_main_layer(self):
        return self.get_layer(self.MAIN_LAYER_NAME)

    def _add_main_layer(self):
        layer = ClubhouseViewMainLayer(self)
        self.add_layer(layer, self.MAIN_LAYER_NAME)

    def _add_info_tip_layer(self):
        layer = ClubhouseViewInfoTipLayer(self)
        self.add_layer(layer, self.INFO_TIP_LAYER)

    def set_scale(self, scale):
        self.scale = scale
        # Update children

        for layer in self.get_children():
            layer.set_scale(self.scale)

    def stop_quest(self):
        self._cancel_ongoing_task()
        self._reset_scheduled_quest()

    def _cancel_ongoing_task(self):
        if self._current_quest is None:
            return

        current_quest = self._current_quest
        # This should be done before calling step_abort to avoid infinite
        # recursion with quests that change can change the hack-mode-enabled
        # like the firstcontact, because setting hack-mode-enabled to false
        # will call to this function and if the quest is not set to None we've
        # the recursion
        self._set_current_quest(None)

        logger.debug('Stopping quest %s', current_quest)
        current_quest.step_abort()

    def _stop_quest_from_message(self, quest):
        if self._is_current_quest(quest):
            self._cancel_ongoing_task()

    def _continue_quest(self, quest):
        if not self._is_current_quest(quest):
            return

        quest.set_to_foreground()
        self._shell_show_current_popup_message()

    def _accept_quest_message(self, new_quest):
        logger.info('Start quest {}'.format(new_quest))
        self._app_window.run_quest(new_quest)

    def connect_quest(self, quest):
        # Don't update the episode if we're running a quest; this is so we avoid reloading the
        # Clubhouse while running a quest if it changes the episode.
        self._gss.handler_block(self._gss_hander_id)

        quest.connect('message', self._quest_message_cb)
        quest.connect('dismiss-message', self._quest_dismiss_message_cb)
        quest.connect('item-given', self._quest_item_given_cb)

    def disconnect_quest(self, quest):
        self._gss.handler_unblock(self._gss_hander_id)
        quest.disconnect_by_func(self._quest_message_cb)
        quest.disconnect_by_func(self._quest_dismiss_message_cb)
        quest.disconnect_by_func(self._quest_item_given_cb)

    def _ask_stop_quest(self, new_quest):

        def accept_stop(new_quest):
            self.run_quest(new_quest)

        def reject_stop():
            Sound.play('clubhouse/dialog/close')
            self._continue_quest(self._current_quest)

        self._shell_popup_message({
            # @todo: This string should not be hardcoded:
            'text': 'You are already in a quest, do you want to start a new one?',
            'system_notification': True,
            'character_id': self.SYSTEM_CHARACTER_ID,
            'character_mood': self.SYSTEM_CHARACTER_MOOD,
            'sound_fx': self.running_quest.proposal_sound,
            'choices': [(self.running_quest.get_label('QUEST_ACCEPT_STOP'), accept_stop, new_quest),
                        (self.running_quest.get_label('QUEST_REJECT_STOP'), reject_stop)],
        })

    def _ask_harder_quest(self, new_quest, easier_quest):

        def accept_harder(new_quest):
            self.run_quest(new_quest)

        def reject_harder():
            Sound.play('clubhouse/dialog/close')

        self._shell_popup_message({
            # @todo: This string should not be hardcoded:
            'text': 'There is an easier quest, do you want to continue anyways?',
            'system_notification': True,
            'character_id': self.SYSTEM_CHARACTER_ID,
            'character_mood': self.SYSTEM_CHARACTER_MOOD,
            'sound_fx': new_quest.proposal_sound,
            'choices': [(new_quest.get_label('QUEST_ACCEPT_HARDER'), accept_harder, new_quest),
                        (new_quest.get_label('QUEST_REJECT_HARDER'), reject_harder)],
        })

    def try_running_quest(self, new_quest, easier_quest=None):
        if self.running_quest is not None and not self.running_quest.stopping:
            self._ask_stop_quest(new_quest)
            return

        if easier_quest is not None:
            self._ask_harder_quest(new_quest, easier_quest)
            return

        self.run_quest(new_quest)

    def run_quest(self, quest):
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

    def _quest_scheduled_cb(self, _registry, quest_name, confirm_before, start_after_timeout):
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
        self._schedule_next_quest()

    def _quest_item_given_cb(self, quest, item_id, text):
        self._shell_popup_item(item_id, text)

    def _quest_message_cb(self, quest, message_info):
        logger.debug('Message %s: %s character_id=%s mood=%s choices=[%s]',
                     message_info['id'], message_info['text'],
                     message_info['character_id'], message_info['character_mood'],
                     '|'.join([answer for answer, _cb, *_args in message_info['choices']]))

        if message_info['type'] == libquest.Quest.MessageType.POPUP:
            self._shell_popup_message(message_info)
        elif message_info['type'] == libquest.Quest.MessageType.NARRATIVE:
            self._app_window.character.message_box.add_message(message_info)

    def _quest_dismiss_message_cb(self, quest, narrative=False):
        if not narrative:
            self._shell_close_popup_message()
        else:
            self._app_window.character.message_box.clear_messages()

    def _reset_delayed_message(self):
        if self._delayed_message_handler > 0:
            GLib.source_remove(self._delayed_message_handler)
            self._delayed_message_handler = 0

    def on_quest_finished(self, quest):
        logger.debug('Quest {} finished'.format(quest))
        self.disconnect_quest(quest)
        self._reset_delayed_message()
        quest.save_conf()

        # Ensure we reset the running quest (only if we haven't started a different quest in the
        # meanwhile) quest and close any eventual message popups
        if self._is_current_quest(quest):
            self._set_current_quest(None)

        if self._current_quest is None:
            self._shell_close_popup_message()
            self._app_window.character.message_box.clear_messages()

        self._current_quest_notification = None

        self._update_episode_if_needed()

        # Ensure the app can be quit if inactive now
        self._app.release()

        # Unhighlight highlighted quests.
        for quest_set in libquest.Registry.get_quest_sets():
            for quest in quest_set.get_quests():
                quest.props.highlighted = False

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
            # @todo: remove confirm_before
            # confirm_before = self._scheduled_quest_info.confirm_before

            self._reset_scheduled_quest()
            self.run_quest(quest)
            return GLib.SOURCE_REMOVE

        timeout = self._scheduled_quest_info.timeout
        self._scheduled_quest_info.handler_id = GLib.timeout_add_seconds(timeout,
                                                                         _run_quest_after_timeout)

    def _shell_close_popup_message(self):
        self._app.close_quest_msg_notification()

    def _shell_popup_message(self, message_info):
        real_popup_message = functools.partial(self._shell_popup_message_real, message_info)

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

    def _shell_popup_message_real(self, message_info):
        notification = Gio.Notification()
        text = message_info.get('text', '')
        notification.set_body(SimpleMarkupParser.parse(text))
        notification.set_title('')

        sfx_sound = message_info.get('sound_fx')
        if sfx_sound:
            Sound.play(sfx_sound)
        bg_sound = message_info.get('sound_bg')
        if self._current_quest and bg_sound != self._current_quest.get_last_bg_sound_event_id():
            self._current_quest.play_stop_bg_sound(bg_sound)

        if self._current_quest and not self._current_quest.dismissible_messages():
            notification.set_priority(Gio.NotificationPriority.URGENT)

        if message_info.get('character_id'):
            character = Character.get_or_create(message_info['character_id'])
            character.mood = message_info['character_mood']

            notification.set_icon(character.get_mood_icon())
            Sound.play('clubhouse/{}/mood/{}'.format(character.id,
                                                     character.mood))

        self._reset_quest_actions()

        for answer in message_info.get('choices', []):
            self._add_quest_action(answer)

        for key, action in self._actions.items():
            label = action[0]
            button_target = "app.quest-user-answer('{}')".format(key)
            notification.add_button(label, button_target)

        self._app.send_quest_msg_notification(notification)

        if not message_info.get('system_notification', False):
            self._current_quest_notification = (notification, self._actions, sfx_sound)

        self._delayed_message_handler = 0
        return GLib.SOURCE_REMOVE

    def _shell_show_current_popup_message(self):
        if self._current_quest_notification is None:
            return

        notification, actions, sound = self._current_quest_notification

        self._recover_quest_actions(actions)

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

    def _recover_quest_actions(self, actions):
        self._actions = actions

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

        for child in self.get_children():
            if isinstance(child, CharacterButton):
                child.destroy()

        libquest.Registry.load_current_episode()
        for quest_set in libquest.Registry.get_quest_sets():
            button = self.get_main_layer().add_quest_set(quest_set)
            self.get_layer(self.INFO_TIP_LAYER).add_info_tip(button)
        self.current_episode = episode_name
        self.get_main_layer().bringup_fg()

    def _update_episode_if_needed(self):
        episode_name = libquest.Registry.get_current_episode()['name']
        if self.current_episode != episode_name:
            self.load_episode(episode_name)

    current_episode = GObject.Property(type=str)
    running_quest = GObject.Property(_get_running_quest,
                                     _set_current_quest,
                                     type=GObject.TYPE_PYOBJECT,
                                     default=None,
                                     flags=GObject.ParamFlags.READABLE |
                                     GObject.ParamFlags.EXPLICIT_NOTIFY)


class ClubhouseViewInfoTipLayer(Gtk.Fixed):

    __gtype_name__ = 'ClubhouseViewInfoTipLayer'

    def __init__(self, clubhouse_view):
        super().__init__(visible=True)
        self.clubhouse_view = clubhouse_view

    def set_scale(self, scale):
        pass

    def add_info_tip(self, quest_set_button):
        infotip = QuestSetInfoTip(quest_set_button)
        self.put(infotip, 0, 0)
        infotip.show_all()

        quest_set_button.connect('enter-notify-event', self._quest_set_button_enter_notify_cb,
                                 infotip)
        quest_set_button.connect('leave-notify-event', self._quest_set_button_leave_notify_cb,
                                 infotip)

    def _quest_set_button_enter_notify_cb(self, quest_set_button, _event, infotip):
        animation = quest_set_button.character.get_body_image().animator.get_current_animation()
        if animation is None:
            return

        button_allocation = quest_set_button.get_allocation()
        infotip_allocation = infotip.get_allocation()

        pivot = animation.get_reference_point('infotip')
        if pivot is None:
            pivot = (button_allocation.width / 2, button_allocation.height / 2)

        x = button_allocation.x + pivot[0] - infotip_allocation.width / 2
        y = button_allocation.y + pivot[1] - infotip_allocation.height / 2

        self.move(infotip, x, y)
        infotip.fade_in()

    def _quest_set_button_leave_notify_cb(self, _quest_set_button, _event, infotip):
        infotip.fade_out()


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/clubhouse-view-main-layer.ui')
class ClubhouseViewMainLayer(Gtk.Fixed):

    __gtype_name__ = 'ClubhouseViewMainLayer'

    _hack_switch = Gtk.Template.Child()
    _hack_switch_panel = Gtk.Template.Child()

    def __init__(self, clubhouse_view):
        super().__init__(visible=True)

        self.clubhouse_view = clubhouse_view
        self._app = Gio.Application.get_default()
        self._app_window = self._app.get_active_window()

        self.add_tick_callback(AnimationSystem.step)

        self._hack_switch.set_active(Desktop.get_hack_mode())
        self._hack_switch_handler_id = self._hack_switch.connect(
            'toggled', self._on_hack_switch_toggled)

        state = ClubhouseState()
        state.connect('notify::hack-switch-highlighted',
                      self._on_hack_switch_highlighted_changed_cb)
        state.connect('notify::lights-on',
                      self._on_lights_changed_cb)

        # Update children allocation
        for child in self.get_children():
            if not isinstance(child, CharacterButton):
                child.size = child.get_size_request()
                child.position = self.child_get(child, 'x', 'y')

    def _on_quest_set_highlighted_changed(self, quest_set, _param):
        if self._app_window.is_visible():
            return

        self._app.send_suggest_open(libquest.Registry.has_quest_sets_highlighted())

    def set_switch_active(self, active=True):
        self._hack_switch.handler_block(self._hack_switch_handler_id)
        self._hack_switch.set_active(active)
        self._hack_switch.handler_unblock(self._hack_switch_handler_id)
        self._update_switch_css()

    def _update_switch_css(self):
        ctx = self._hack_switch_panel.get_style_context()
        if self._hack_switch.get_active():
            ctx.remove_class('off')
        else:
            ctx.add_class('off')

    def _on_hack_switch_toggled(self, button):
        mock_quests = ['Quickstart', 'Migration', 'Meet']
        mock_hack_mode = (self._app_window.clubhouse.running_quest is not None and
                          self._app_window.clubhouse.running_quest.get_id() in mock_quests)
        if mock_hack_mode:
            self._app_window._clubhouse_state.lights_on = button.get_active()
        else:
            Desktop.set_hack_mode(button.get_active())

            # Recording Hack switch event
            recorder = EosMetrics.EventRecorder.get_default()
            hack_mode = GLib.Variant('b', button.get_active())
            recorder.record_event(HACK_MODE_EVENT, hack_mode)

        self._update_switch_css()

    def _on_lights_changed_cb(self, state, _param):
        if state.lights_on != self._hack_switch.get_active():
            self.set_switch_active(state.lights_on)

    def _on_hack_switch_highlighted_changed_cb(self, state, _param):
        ctx = self._hack_switch.get_style_context()
        if state.hack_switch_highlighted:
            ctx.add_class('highlighted')
        else:
            ctx.remove_class('highlighted')

    def _update_child_position(self, child):
        if isinstance(child, CharacterButton):
            x, y = child.position
            self.move(child, x, y)

    def set_scale(self, scale):
        self.scale = scale
        # Update children
        for child in self.get_children():
            if isinstance(child, CharacterButton):
                child.reload(self.scale)
            else:
                x, y = child.position
                child.set_size_request(child.size.width * scale,
                                       child.size.height * scale)
                self.move(child, x * scale, y * scale)

    def add_quest_set(self, quest_set):
        button = CharacterButton(quest_set, self.clubhouse_view.scale)
        quest_set.connect('notify::highlighted', self._on_quest_set_highlighted_changed)
        button.connect('clicked', self._quest_set_button_clicked_cb)

        x, y = button.position
        self.put(button, x, y)

        button.connect('notify::position', self._on_button_position_changed)
        return button

    def bringup_fg(self):
        fg = []
        for child in self.get_children():
            if not isinstance(child, CharacterButton):
                fg.append(child)
                self.remove(child)

        for child in fg:
            x, y = child.position
            self.put(child, x * self.scale, y * self.scale)

    def _on_button_position_changed(self, button, _param):
        self._update_child_position(button)

    def _quest_set_button_clicked_cb(self, button):
        quest_set = button.get_quest_set()
        self._app_window.character.show_mission_list(quest_set)
        self._app_window.set_page('CHARACTER')

        recorder = EosMetrics.EventRecorder.get_default()
        character = GLib.Variant('s', quest_set.get_character())
        recorder.record_event(CLUBHOUSE_PATHWAY_ENTER_EVENT, character)


class FixedLabel(Gtk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_get_preferred_width(self):
        return self.props.width_request, self.props.width_request


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/news-item.ui')
class NewsItem(Gtk.Box):

    __gtype_name__ = 'NewsItem'

    _title_label = Gtk.Template.Child()
    _date_label = Gtk.Template.Child()
    _character_image = Gtk.Template.Child()
    _text_box = Gtk.Template.Child()
    _image_button = Gtk.Template.Child()
    _image = Gtk.Template.Child()

    def __init__(self, data):
        super().__init__()

        self.date = data.date

        self._title_label.set_label('@' + data.character.capitalize())

        self._text_label = FixedLabel(wrap=True,
                                      visible=True,
                                      use_markup=True,
                                      xalign=0,
                                      yalign=0,
                                      width_request=480)
        self._text_box.add(self._text_label)

        self._text_label.props.label = data.text
        self._date_label.props.label = self._get_human_date(data.date)

        character = os.path.join(config.NEWSFEED_DIR, 'avatar', data.character)
        self._character_image.set_from_file(character)

        if data.image != '':
            image = os.path.join(config.NEWSFEED_DIR, data.image)
            self._image.set_from_file(image)
            self._image_button.set_uri(data.image_href)
            self._image_button.show()

    def _get_human_date(self, date):
        today = datetime.date.today()

        if date == today:
            return 'Today'
        elif date == today - datetime.timedelta(days=1):
            return 'Yesterday'
        elif date.year == today.year:
            return date.strftime('%B %d')
        else:
            return date.strftime('%B %d %Y')


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/news-view.ui')
class NewsView(Gtk.Overlay):

    __gtype_name__ = 'NewsView'

    _news_box = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self._app = Gio.Application.get_default()
        self._news_db = utils.NewsFeedDB()
        self._populate_news()
        self._update_news_visivility()

    def _populate_news(self):
        for data in self._news_db.get_list():
            item = NewsItem(data)
            self._news_box.pack_start(item, True, False, 0)

    def _update_news_visivility(self):
        today = datetime.date.today()

        for child in self._news_box.get_children():
            if (child.date <= today) or self._app.has_debug('newsfeed'):
                child.show()
            else:
                child.hide()

        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        timeout = datetime.datetime.combine(tomorrow, datetime.time.min) - now

        # Update news visibility one minute after midnight
        GLib.timeout_add_seconds(timeout.total_seconds() + 60,
                                 self._update_news_visivility)

        return GLib.SOURCE_REMOVE


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/achievement-item.ui')
class AchievementItem(Gtk.Box):

    __gtype_name__ = 'AchievementItem'

    DEFAULT_BADGE_SIZE = 128

    _image = Gtk.Template.Child()

    def __init__(self, achievement):
        super().__init__()

        self._achievement = achievement

        badge_dir = os.path.join(config.ACHIEVEMENTS_DIR, 'badges')

        default_image_path = os.path.join(badge_dir, '{}.svg'.format(achievement.id))
        hover_image_path = os.path.join(badge_dir, '{}-hover.svg'.format(achievement.id))

        self._default_pixbuf = self._create_pixbuf(default_image_path)
        try:
            self._hover_pixbuf = self._create_pixbuf(hover_image_path)
        except GLib.Error as ex:
            logger.warning('Cannot create hover image for achievement \'%s\', becuase: %s',
                           self._achievement.id, ex)
            self._hover_pixbuf = None

        self.set_default_image()

    def set_default_image(self):
        self._image.set_from_pixbuf(self._default_pixbuf)

    def set_hover_image(self):
        if self._hover_pixbuf is not None:
            self._image.set_from_pixbuf(self._hover_pixbuf)

    def _create_pixbuf(self, image_path):
        return GdkPixbuf.Pixbuf.new_from_file_at_scale(image_path, -1, self.DEFAULT_BADGE_SIZE,
                                                       True)

    def _get_achievement(self):
        return self._achievement

    achievement = property(_get_achievement)


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/achievement-flow-box-child.ui')
class AchievementFlowBoxChild(Gtk.FlowBoxChild):

    __gtype_name__ = 'AchievementFlowBoxChild'

    _event_box = Gtk.Template.Child()

    def __init__(self, achievement):
        super().__init__()
        item = AchievementItem(achievement)
        self._event_box.add(item)

    def get_item(self):
        children = self._event_box.get_children()
        if not children or not isinstance(children[0], AchievementItem):
            return None
        return children[0]

    @Gtk.Template.Callback()
    def _event_box_enter_notify_event_cb(self, _child, _event):
        item = self.get_item()
        if not item:
            return
        item.set_hover_image()

    @Gtk.Template.Callback()
    def _event_box_leave_notify_event_cb(self, _child, _event):
        item = self.get_item()
        if not item:
            return
        item.set_default_image()


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/achievement-summary-view.ui')
class AchievementSummaryView(Gtk.Box):

    __gtype_name__ = 'AchievementSummaryView'

    DEFAULT_BADGE_SIZE = 128

    _image = Gtk.Template.Child()
    _title_label = Gtk.Template.Child()
    _summary_label = Gtk.Template.Child()

    def __init__(self):
        super().__init__()
        self._title_label.set_line_wrap(True)
        self._summary_label.set_line_wrap(True)

    def update_from_achievement(self, achievement):
        badge_dir = os.path.join(config.ACHIEVEMENTS_DIR, 'badges')
        image_path = os.path.join(badge_dir, '{}.svg'.format(achievement.id))

        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(image_path, -1,
                                                         self.DEFAULT_BADGE_SIZE,
                                                         True)
        self._image.set_from_pixbuf(pixbuf)
        self._title_label.props.label = achievement.name
        self._summary_label.props.label = achievement.description


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/achievements-view.ui')
class AchievementsView(Gtk.Box):

    __gtype_name__ = 'AchievementsView'

    DEFAULT_TRIANGLE_HEIGHT = 30
    PAGE_GRID = 'GRID'
    PAGE_SUMMARY = 'SUMMARY'

    _event_box = Gtk.Template.Child()
    _title_box = Gtk.Template.Child()
    _title_box_box = Gtk.Template.Child()
    _title_box_icon_revealer = Gtk.Template.Child()
    _achievements_flow_box = Gtk.Template.Child()
    _achievement_summary_box = Gtk.Template.Child()
    _stack = Gtk.Template.Child()
    _grid_scrolled_window = Gtk.Template.Child()
    _summary_scrolled_window = Gtk.Template.Child()

    def __init__(self, app_window):
        super().__init__()
        self._app_window = app_window
        self._hover = False
        self._shape_points = None

        self._manager = AchievementsDB().manager
        self._achievements_achieved_id = None

        if self._manager.empty_state_achievement is not None:
            self._add_achievement(self._manager.empty_state_achievement)

        self._achievement_summary_view = AchievementSummaryView()
        self._achievement_summary_box.add(self._achievement_summary_view)
        self._achievement_summary_view.show_all()

        self._app_window.clubhouse.connect('notify::current-episode',
                                           self._current_episode_changed_cb)

        self._event_box.connect('motion-notify-event', self._motion_notify_event_cb)
        self._event_box.connect('leave-notify-event', self._leave_notify_event_cb)

        self.connect('notify::current-achievement', self._current_achievement_notify_cb)

    def set_page(self, page):
        if page == self.PAGE_SUMMARY:
            if not self.current_achievement:
                logger.warning('No current achievement')
                return
            self._achievement_summary_view.update_from_achievement(self.current_achievement)
            self._title_box_icon_revealer.props.reveal_child = True
        elif page == self.PAGE_GRID:
            self._title_box_icon_revealer.props.reveal_child = False
        else:
            logger.error('Error when setting page in AchievementsView: page \'%s\' does not exist.',
                         page)

        self._stack.props.visible_child_name = page

    def reset_scrollbar_position(self):
        self._grid_scrolled_window.props.vadjustment.props.value = 0
        self._summary_scrolled_window.props.vadjustment.props.value = 0

    def show_achievement(self, achievement_id):
        for child in self._achievements_flow_box.get_children():
            item = child.get_item()

            if not item:
                continue

            if item.achievement.id == achievement_id:
                self.current_achievement = item.achievement
                return

    def get_current_page(self):
        return self._stack.props.visible_child_name

    def _current_episode_changed_cb(self, _window, _pspec):
        if self._achievements_achieved_id is not None:
            self._manager.disconnect(self._achievements_achieved_id)
        self._populate()
        self._achievements_achieved_id = \
            self._manager.connect('achievement-achieved',
                                  lambda _manager, achievement: self._give_achievement(achievement))

    def _populate(self):
        for achievement in self._manager.get_achievements_achieved():
            self._add_achievement(achievement)

    def _give_achievement(self, achievement):
        self._shell_popup_achievement_badge(achievement)
        self._add_achievement(achievement)

    def _shell_popup_achievement_badge(self, achievement):
        notification = Gio.Notification()

        template_text = utils.QuestStringCatalog.get_string('NOQUEST_GIVE_BADGE')
        if template_text is None:
            template_text = 'Got new badge *{{achievement.name}}*'

        template = utils.MessageTemplate(template_text)
        text = template.substitute({'achievement.name': achievement.name})
        notification.set_body(SimpleMarkupParser.parse(text))
        notification.set_title('')

        icon_path = os.path.join(config.ACHIEVEMENTS_DIR, 'badges', '{}.svg'.format(achievement.id))
        icon_file = Gio.File.new_for_path(icon_path)
        icon_bytes = icon_file.load_bytes(None)
        icon = Gio.BytesIcon.new(icon_bytes[0])

        notification.add_button('OK', f"app.badge-notification(('{achievement.id}', false))")
        notification.add_button('Show me', f"app.badge-notification(('{achievement.id}', true))")

        notification.set_icon(icon)
        Gio.Application.get_default().send_quest_item_notification(notification)

    def _add_achievement(self, achievement):
        try:
            achievement_item = AchievementFlowBoxChild(achievement)
        except GLib.Error as ex:
            logger.warning('Achievement %s will not be shown because of an error: %s',
                           achievement.name, ex)
            return

        self._achievements_flow_box.add(achievement_item)
        self._achievements_flow_box.show_all()

    def do_draw(self, cr):
        self._undraw_bottom_triangle(cr)
        Gtk.Box.do_draw(self, cr)

    def _undraw_bottom_triangle(self, cr):
        allocation = self.get_allocation()

        self._shape_points = [
            (0, 0),
            (allocation.width, 0),
            (allocation.width, allocation.height),
            (allocation.width / 2, allocation.height - self.DEFAULT_TRIANGLE_HEIGHT),
            (0, allocation.height)
        ]

        cr.move_to(*self._shape_points[0])
        for point in self._shape_points[1:]:
            cr.line_to(*point)
        cr.clip()

    def _get_hover(self):
        return self._hover

    def _motion_notify_event_cb(self, _view, event):
        self._hover = self._event_coordinates_in_shape(event)

    def _event_coordinates_in_shape(self, event):
        p = (event.x, event.y)

        allocation = self.get_allocation()
        tl = (allocation.x, allocation.y)
        tr = (allocation.x + allocation.width, allocation.y)
        br = (allocation.x + allocation.width, allocation.y + allocation.height)
        in_rectangle = p[0] > tl[0] and p[0] < tr[0] and p[1] > tl[1] and p[1] < br[1]
        if not in_rectangle:
            return False

        a = self._shape_points[-1]
        b = self._shape_points[-2]
        c = self._shape_points[-3]
        # @todo: Find a way to avoid manually adding the top widget height.
        p = (p[0], p[1] + self._title_box.get_allocation().height)
        in_triangle = utils.inside_triangle(p, a, b, c)
        return not in_triangle

    def _leave_notify_event_cb(self, _view, event):
        # Instead of setting self._hover directly to False, we double check, becuase
        # for some reason this callbacks gets called when you click inside the
        # AchievementsView for the secnd time.
        self._hover = self._event_coordinates_in_shape(event)

    @Gtk.Template.Callback()
    def _achievements_flow_box_child_activated_cb(self, _view, achievment_flow_box_child):
        item = achievment_flow_box_child.get_item()
        if not item:
            return
        self.current_achievement = item.achievement

    def _current_achievement_notify_cb(self, _view, _pspec):
        if self.current_achievement is None:
            page = self.PAGE_GRID
        else:
            page = self.PAGE_SUMMARY
        self.set_page(page)

    @Gtk.Template.Callback()
    def _title_box_event_box_enter_notify_event_cb(self, box, _event):
        if self.get_current_page() == self.PAGE_SUMMARY:
            ctx = box.get_style_context()
            ctx.add_class('hover')

    @Gtk.Template.Callback()
    def _title_box_event_box_leave_notify_event_cb(self, box, _event):
        if self.get_current_page() == self.PAGE_SUMMARY:
            ctx = box.get_style_context()
            ctx.remove_class('hover')

    @Gtk.Template.Callback()
    def _title_box_event_box_button_press_event_cb(self, box, _event):
        if self.get_current_page() == self.PAGE_SUMMARY:
            ctx = box.get_style_context()
            ctx.remove_class('hover')
            self.set_page(self.PAGE_GRID)

    current_achievement = GObject.Property(type=object, default=None)
    hover = property(_get_hover)


@Gtk.Template.from_resource('/com/hack_computer/Clubhouse/clubhouse-window.ui')
class ClubhouseWindow(Gtk.ApplicationWindow):

    __gtype_name__ = 'ClubhouseWindow'
    _MAIN_PAGE_RESET_TIMEOUT = 60  # sec
    _AMBIENT_SOUND_DURATION_SECONDS = 120

    _headerbar = Gtk.Template.Child()
    _headerbar_box = Gtk.Template.Child()
    _stack = Gtk.Template.Child()
    _stack_event_box = Gtk.Template.Child()

    _user_box = Gtk.Template.Child()
    _user_box_event_box = Gtk.Template.Child()
    _user_button = Gtk.Template.Child()
    _user_event_box = Gtk.Template.Child()
    _user_label = Gtk.Template.Child()
    _user_button_image_revealer = Gtk.Template.Child()
    _user_image_button = Gtk.Template.Child()
    _achievements_view_box = Gtk.Template.Child()
    _achievements_view_revealer = Gtk.Template.Child()
    _achievements_view_revealer_revealer = Gtk.Template.Child()

    _pathways_menu_button = Gtk.Template.Child()
    _clubhouse_button = Gtk.Template.Child()
    _hack_news_button = Gtk.Template.Child()

    def __init__(self, app):
        super().__init__(application=app, title='Clubhouse')

        self._gss = GameStateService()
        self._user = UserAccount()
        self._page_reset_timeout = 0

        self._ambient_sound_item = SoundItem('clubhouse/ambient')
        self._play_ambient_sound = True
        self._ambient_sound_timer_id = None

        self.clubhouse = ClubhouseView(self)
        self.news = NewsView()
        self.character = CharacterView(self)

        self._achievements_view = AchievementsView(self)
        self._achievements_view_revealer.add(self._achievements_view)

        self._stack_event_box.connect('button-press-event',
                                      lambda _box, _event: self.hide_achievements_view())
        self._user_box_event_box.connect('button-press-event',
                                         self._user_event_box_button_press_event_cb,
                                         self._achievements_view)

        self._stack.add_named(self.clubhouse, 'CLUBHOUSE')
        self._stack.add_named(self.news, 'NEWS')
        self._stack.add_named(self.character, 'CHARACTER')

        self._clubhouse_state = ClubhouseState()
        self._clubhouse_state.connect('notify::window-is-visible',
                                      self._on_clubhouse_window_visibility_changed_cb)
        self._clubhouse_state.connect('notify::nav-attract-state',
                                      self._on_clubhouse_nav_attract_state_changed_cb)
        self._clubhouse_state.connect('notify::user-button-highlighted',
                                      self._on_user_button_highlighted_changed_cb)
        self._clubhouse_state.connect('notify::lights-on',
                                      self._on_lights_changed_cb)

        self.sync_with_hack_mode()
        Desktop.shell_settings_connect('changed::{}'.format(Desktop.SETTINGS_HACK_MODE_KEY),
                                       self._hack_mode_changed_cb)

        self.connect('screen-changed', self._on_screen_changed)
        self._on_screen_changed(None, None)

        self._css_provider = Gtk.CssProvider()
        self.get_style_context().add_provider_for_screen(
            Gdk.Screen.get_default(),
            self._css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1)

        self._user.connect('changed', lambda _user: self.update_user_info())
        self.update_user_info()

    def _user_event_box_button_press_event_cb(self, _button, event, achievements_view):
        if not achievements_view.hover:
            self.hide_achievements_view()

    def sync_with_hack_mode(self):
        hack_mode_enabled = Desktop.get_hack_mode()
        if not hack_mode_enabled:
            self.clubhouse.stop_quest()

        self._clubhouse_state.lights_on = hack_mode_enabled

    def _hack_mode_changed_cb(self, _settings, _key):
        self.sync_with_hack_mode()

    def _on_user_button_highlighted_changed_cb(self, state, _param):
        context = self._user_button.get_style_context()
        if state.user_button_highlighted:
            context.add_class('button-attract')
        else:
            context.remove_class('button-attract')

    def _on_lights_changed_cb(self, state, _param):
        lights_on = self._clubhouse_state.lights_on
        Desktop.set_hack_background(lights_on)
        Desktop.set_hack_cursor(lights_on)
        self._pathways_menu_button.props.sensitive = lights_on

        ctx = self.get_style_context()
        ctx.add_class('transitionable-background')

        if lights_on:
            ctx.remove_class('off')
            if self.props.visible:
                self.play_ambient_sound()
        else:
            ctx.add_class('off')
            self.hide_achievements_view()
            self.stop_ambient_sound()

    def _update_window_size(self):
        BG_WIDTH = 1304
        BG_HEIGHT = 864

        screen = self.get_screen()
        if screen is None:
            return

        screen_height = screen.get_height()

        # Remove small/big css classes
        context = self.get_style_context()
        context.remove_class('small')
        context.remove_class('big')

        # Add class depending on screen size
        if screen_height <= 720:
            context.add_class('small')
            factor = 0.94
        elif screen_height >= 1080:
            context.add_class('big')
            factor = 0.8
        else:
            factor = 0.85

        # Clamp resolution to 80% of 720p-1080p
        height = max(720, min(screen_height, 1080)) * factor

        # Set main box size
        self.set_size_request(height * BG_WIDTH / BG_HEIGHT, height)

        scale = height / BG_HEIGHT
        self.clubhouse.set_scale(scale)
        self.character.set_scale(scale)

    def _on_screen_size_changed(self, screen):
        self._update_window_size()

    def _on_screen_changed(self, widget, previous_screen):
        screen = self.get_screen()

        if previous_screen is not None:
            previous_screen.disconnect_by_func(self._on_screen_size_changed)

        if screen is not None:
            self.set_visual(screen.get_rgba_visual())
            screen.connect('size-changed', self._on_screen_size_changed)
            self._update_window_size()

    def _on_clubhouse_window_visibility_changed_cb(self, state, _param):
        if state.window_is_visible:
            self.show()
        else:
            self.hide()

    def _on_clubhouse_nav_attract_state_changed_cb(self, state, _param):
        self._clubhouse_button.get_style_context().remove_class('nav-attract')
        self._pathways_menu_button.get_style_context().remove_class('nav-attract')
        self._hack_news_button.get_style_context().remove_class('nav-attract')

        if state.nav_attract_state == ClubhouseState.Page.CLUBHOUSE:
            self._clubhouse_button.get_style_context().add_class('nav-attract')
        elif state.nav_attract_state == ClubhouseState.Page.PATHWAYS:
            self._pathways_menu_button.get_style_context().add_class('nav-attract')
        elif state.nav_attract_state == ClubhouseState.Page.NEWS:
            self._hack_news_button.get_style_context().add_class('nav-attract')

    def update_user_info(self):
        real_name = self._user.get('RealName')
        icon_file = self._user.get('IconFile')

        default_avatar_path = '/var/lib/AccountsService/icons'
        if not icon_file.startswith(default_avatar_path):
            icon_file = '/var/run/host/{}'.format(icon_file)

        self._user_label.set_label(real_name)

        if icon_file and os.path.exists(icon_file):
            self._user_image_button.set_label('')
            self._css_provider.load_from_data("#image.user-overlay {{\
                background-image: url('{}');\
            }}".format(icon_file).encode())
        else:
            tokens = real_name.split(' ')

            if len(tokens) > 1:
                initials = tokens[0][0] + tokens[-1][0]
            else:
                initials = tokens[0][0]

            self._user_image_button.set_label(initials.upper())
            self._css_provider.load_from_data(''.encode())

    @Gtk.Template.Callback()
    def _on_button_press_event(self, widget, e):
        if e.button != Gdk.BUTTON_PRIMARY:
            return False

        self.begin_move_drag(e.button, e.x_root, e.y_root, e.time)
        self.hide_achievements_view()
        return True

    @Gtk.Template.Callback()
    def _on_delete(self, widget, _event):
        widget.hide()
        return True

    def set_page(self, page_name):
        current_page = self._stack.get_visible_child_name()
        new_page = page_name.upper()

        if current_page == new_page:
            return

        if page_name == 'CLUBHOUSE':
            self._clubhouse_button.set_active(True)
        elif page_name == 'NEWS':
            self._hack_news_button.set_active(True)

        if current_page == 'CHARACTER':
            running_quest = self.clubhouse.running_quest
            if running_quest is not None and running_quest.is_narrative():
                running_quest.step_abort()

        # Set a different css class depending on the page
        ctx = self.get_style_context()
        ctx.remove_class(current_page)
        ctx.add_class(new_page)

        ctx.remove_class('transitionable-background')

        # Set custom headerbar content from current page
        page = self._stack.get_child_by_name(new_page)

        self._clubhouse_state.current_page = ClubhouseState.Page[new_page]

        # The CHARACTER page disables the PATHWAY nav attract state
        nav_page = 'PATHWAYS' if new_page == 'CHARACTER' else new_page
        nav_page = ClubhouseState.Page[nav_page]
        if self._clubhouse_state.nav_attract_state == nav_page:
            self._clubhouse_state.nav_attract_state = None

        if hasattr(page, 'header_box') and page.header_box is not None:
            width = self._headerbar_box.get_allocated_width()
            page.header_box.set_size_request(width, -1)
            page.header_box.get_style_context().add_class(new_page)
            self._headerbar.set_custom_title(page.header_box)
        else:
            self._headerbar.set_custom_title(self._headerbar_box)

        # Switch page
        self._stack.set_visible_child(page)
        self.hide_achievements_view()

        recorder = EosMetrics.EventRecorder.get_default()
        page_variant = GLib.Variant('s', new_page)
        recorder.record_event(CLUBHOUSE_SET_PAGE_EVENT, page_variant)

    def _select_main_page_on_timeout(self):
        self.set_page('CLUBHOUSE')
        self._page_reset_timeout = 0

        return GLib.SOURCE_REMOVE

    def _stop_page_reset_timeout(self):
        if self._page_reset_timeout > 0:
            GLib.source_remove(self._page_reset_timeout)
            self._page_reset_timeout = 0

    def _reset_selected_page_on_timeout(self):
        self._stop_page_reset_timeout()

        if self._stack.get_visible_child() == self.clubhouse:
            return

        self._page_reset_timeout = GLib.timeout_add_seconds(self._MAIN_PAGE_RESET_TIMEOUT,
                                                            self._select_main_page_on_timeout)

    @Gtk.Template.Callback()
    def _user_button_clicked_cb(self, _user_button):
        context = _user_button.get_style_context()
        if context.has_class('button-attract'):
            context.remove_class('button-attract')

        revealer = self._achievements_view_revealer_revealer
        if not revealer.props.reveal_child:
            revealer.props.reveal_child = \
                Desktop.get_hack_mode() and not revealer.props.reveal_child
        else:
            self.hide_achievements_view()

    @Gtk.Template.Callback()
    def _achievements_view_revealer_revealer_child_revealed_notify_cb(self, revealer, _pspec):
        if revealer.props.child_revealed:
            self._user_button_image_revealer.props.reveal_child = True
            self._achievements_view_revealer.props.reveal_child = True
            # Set the achievements view to its default state.
            self._achievements_view.set_page(AchievementsView.PAGE_GRID)
            self._achievements_view.reset_scrollbar_position()

    @Gtk.Template.Callback()
    def _achievements_view_revealer_child_revealed_notify_cb(self, revealer, _pspec):
        if not revealer.props.child_revealed:
            self._user_button_image_revealer.props.reveal_child = False
            self._achievements_view_revealer_revealer.props.reveal_child = False

    def hide_achievements_view(self):
        self._achievements_view_revealer.props.reveal_child = False

    @Gtk.Template.Callback()
    def _on_visibile_property_changed(self, _window, _param):
        if self.props.visible:
            self._stop_page_reset_timeout()
            self.play_ambient_sound()
        else:
            self._reset_selected_page_on_timeout()
            self.stop_ambient_sound()

        self._clubhouse_state.window_is_visible = self.props.visible

    def play_ambient_sound(self):
        hack_mode_enabled = Desktop.get_hack_mode()

        if not self._play_ambient_sound and hack_mode_enabled:
            self._play_ambient_sound = True

        if not self._play_ambient_sound or not hack_mode_enabled:
            return

        self._ambient_sound_item.play()
        # The sound will be stopped after certain time.
        if self._ambient_sound_timer_id is None:
            self._ambient_sound_timer_id = \
                GLib.timeout_add_seconds(self._AMBIENT_SOUND_DURATION_SECONDS,
                                         self._ambient_sound_timer_cb)

    def _ambient_sound_timer_cb(self):
        self.stop_ambient_sound()
        self._play_ambient_sound = False
        self._ambient_sound_timer_id = None
        return GLib.SOURCE_REMOVE

    def stop_ambient_sound(self):
        self._ambient_sound_item.stop()

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
                         resource_base_path='/com/hack_computer/Clubhouse')

        self._window = None
        self._debug = {}
        self._registry_loaded = False
        self._suggesting_open = False
        self._session_mode = None
        self._cards_path = None

        self.add_main_option('list-quests', ord('q'), GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'List existing quest sets and quests', None)
        self.add_main_option('list-episodes', 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'List available episodes', None)
        self.add_main_option('get-episode', 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'Print the current episode', None)
        self.add_main_option('set-episode', 0, GLib.OptionFlags.NONE, GLib.OptionArg.STRING,
                             'Switch to this episode, marking it as not complete', 'EPISODE_NAME')
        self.add_main_option('set-quest', 0, GLib.OptionFlags.NONE, GLib.OptionArg.STRING,
                             'Start a quest.',
                             '[EPISODE_NAME.]QUEST_NAME')
        self.add_main_option('reset', 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'Reset all quests state and game progress', None)
        self.add_main_option('debug', ord('d'), GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'Set debug level in logs.', None)
        self.add_main_option('debug-newsfeed', 0, GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'Turn on debug in newsfeed, displaying all items.', None)
        self.add_main_option('quit', ord('x'), GLib.OptionFlags.NONE, GLib.OptionArg.NONE,
                             'Fully close the application', None)

    def _init_style(self):
        css_file = Gio.File.new_for_uri('resource:///com/hack_computer/Clubhouse/gtk-style.css')
        css_provider = Gtk.CssProvider()
        css_provider.load_from_file(css_file)
        style_context = Gtk.StyleContext()
        style_context.add_provider_for_screen(Gdk.Screen.get_default(),
                                              css_provider,
                                              Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    @Performance.timeit
    def do_activate(self):
        self._ensure_registry_loaded()
        self._ensure_suggesting_open()
        self._init_style()

        if not self._run_episode_autorun_quest_if_needed():
            self._ensure_window()
            self.show(Gdk.CURRENT_TIME)
            self._show_and_focus_window()
        else:
            # Workaround for https://phabricator.endlessm.com/T28479
            mail_layer = self._window.clubhouse.get_main_layer()
            mail_layer.set_switch_active()

    def _run_episode_autorun_quest_if_needed(self):
        autorun_quest = libquest.Registry.get_autorun_quest()
        if autorun_quest is not None:
            # Run the quest in the app's main instance
            self.activate_action('run-quest', GLib.Variant('(sb)', (autorun_quest, True)))
            return True

        libquest.Registry.try_offer_quest()

        return False

    def do_handle_local_options(self, options):
        self.register(None)

        if options.contains('list-quests'):
            self._ensure_registry_loaded()
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

            # The quest can be set with the episode name prefix, e.g. hack2.Meet .
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
            self.activate_action('debug-logs', GLib.Variant('b', True))
            return 0

        if options.contains('debug-newsfeed'):
            self.activate_action('debug-newsfeed', GLib.Variant('b', True))
            return 0

        if options.contains('quit'):
            self.activate_action('quit', None)
            return 0

        return -1

    def do_startup(self):
        Gtk.Application.do_startup(self)

        simple_actions = [('badge-notification', self._badge_notification_action_cb,
                           GLib.VariantType.new('(sb)')),
                          ('debug-logs', self._debug_logs_action_cb, GLib.VariantType.new('b')),
                          ('debug-newsfeed', self._debug_newsfeed_action_cb,
                           GLib.VariantType.new('b')),
                          ('quest-user-answer', self._quest_user_answer, GLib.VariantType.new('s')),
                          ('quest-view-close', self._quest_view_close_action_cb, None),
                          ('quit', self._quit_action_cb, None),
                          ('close', self._close_action_cb, None),
                          ('run-quest', self._run_quest_action_cb, GLib.VariantType.new('(sb)')),
                          ('show-page', self._show_page_action_cb, GLib.VariantType.new('s')),
                          ('show-character', self._show_character_action_cb,
                           GLib.VariantType.new('s')),
                          ('stop-quest', self._stop_quest, None),
                          ]

        for name, callback, variant_type, *callback_args in simple_actions:
            action = Gio.SimpleAction.new(name, variant_type)
            action.connect('activate', callback, *callback_args)
            self.add_action(action)

    def _badge_notification_action_cb(self, action, arg_variant):
        achievement_id, show = arg_variant.unpack()

        # Does nothing if we don't want to show, this will just dismiss the
        # notification
        if not show:
            return

        self._ensure_window()
        self._window.set_page('CLUBHOUSE')
        self.show(Gdk.CURRENT_TIME)
        revealer = self._window._achievements_view_revealer_revealer
        if not revealer.props.reveal_child:
            revealer.props.reveal_child = True

        self._window._achievements_view.show_achievement(achievement_id)

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

    def _load_episode(self):
        # @todo: Move staff from clubhouse_page.load_episode() here
        self._window.clubhouse.load_episode()

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

    def _debug_logs_action_cb(self, action, arg_variant):
        logger.setLevel(logging.DEBUG)
        self._ensure_window()

    def _debug_newsfeed_action_cb(self, action, arg_variant):
        self._debug['newsfeed'] = arg_variant.unpack()
        self._ensure_window()

    def _quest_user_answer(self, action, action_id):
        if self._window:
            self._window.clubhouse.quest_action(action_id.unpack())

    def _quest_view_close_action_cb(self, _action, _action_id):
        logger.debug('Shell quest view closed')
        self._stop_quest()

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

    def _show_character_action_cb(self, action, arg_variant):
        character_id = arg_variant.unpack()
        if self._window:
            qs = libquest.Registry.get_questset_for_character(character_id)
            self._window.character.show_mission_list(qs)
            self._window.set_page('CHARACTER')
            self._show_and_focus_window()

            recorder = EosMetrics.EventRecorder.get_default()
            recorder.record_event(CLUBHOUSE_PATHWAY_ENTER_EVENT, arg_variant)

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

    def has_debug(self, mode):
        return self._debug.get(mode, False)

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

    # D-Bus implementation
    def migrationQuest(self):
        MIGRATION_QUEST = 'Migration'

        self._ensure_registry_loaded()

        # Check if this is done, in that case, do nothing
        quest = libquest.Registry.get_quest_by_name(MIGRATION_QUEST)
        if quest.complete:
            return

        # Mark first contact quest (HackUnlock) as done
        for quest_id in ['FirstContact', 'Quickstart']:
            quest = libquest.Registry.get_quest_by_name(quest_id)
            quest.complete = True
            quest.save_conf()

        OldGameStateService().migrate()
        gss = GameStateService()
        keys = [
            'lock.OperatingSystemApp.1',
            'lock.OperatingSystemApp.2',
            'lock.OperatingSystemApp.3'
        ]
        for key in keys:
            gss.set_async(key, {'locked': False})

        # This write the local flatpak override for old and new hack apps
        Desktop.set_hack_mode(True)
        # Launch the clubhouse window and the migration quest!
        # This quest can make the hack icon bounce
        self._run_quest_by_name(MIGRATION_QUEST)

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

        libquest.Registry.set_current_episode(episode_name, force=True)
        libquest.Registry.load_current_episode()

        print('Setting up {} as available'.format(quest_id))
        self._run_quest_by_name(quest_id)

    def _reset(self):
        try:
            subprocess.run(config.RESET_SCRIPT_PATH, check=True)
            return 0
        except subprocess.CalledProcessError as e:
            logger.warning('Could not reset the Clubhouse: %s', e)
            return 1


# Set widget classes CSS name to be able to select by GType name
clubhouse_classes = [
    AchievementFlowBoxChild,
    AchievementItem,
    AchievementSummaryView,
    AchievementsView,
    CharacterView,
    ClubhouseView,
    ClubhouseViewMainLayer,
    ClubhouseWindow,
    Message,
    MessageButton,
    NewsItem,
    NewsView,
    ActivityCard,
    CharacterButton,
    QuestSetInfoTip
]

for klass in clubhouse_classes:
    klass.set_css_name(klass.__gtype_name__)

if __name__ == '__main__':
    app = ClubhouseApplication()
    app.run(sys.argv)
