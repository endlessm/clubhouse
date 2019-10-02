import glob
import json
import os
import random

from gi.repository import Gio, GLib, Gtk, GObject, GdkPixbuf

from enum import Enum
from eosclubhouse import config, logger

# The default delay if not provided in the animation metadata:
DEFAULT_DELAY = 100


def _get_alternative_characters_dir():
    return os.path.join(GLib.get_user_data_dir(), 'characters')


def get_character_animation_dirs(subpath):
    return [os.path.join(config.CHARACTERS_DIR, subpath),
            os.path.join(_get_alternative_characters_dir(), subpath)]


class AnimationImage(Gtk.Image):
    def __init__(self, subpath):
        super().__init__()
        self._animator = Animator(self)
        self._subpath = subpath

    def load(self, scale=1):
        self._animator.load(self._subpath, None, scale)

    def play(self, name):
        self._animator.play(name)

    def get_anchor(self):
        animation = self._animator.get_current_animation()
        if animation is None:
            return (0, 0)
        return animation.anchor


class Animator(GObject.GObject):

    def __init__(self, target_image):
        super().__init__()
        self._animations = {}
        self._pending_animations = {}
        self._target_image = target_image
        self._animation_after_load = None

    def _do_load(self, subpath, prefix=None, scale=1):
        for sprites_path in get_character_animation_dirs(subpath):
            for sprite in glob.glob(os.path.join(sprites_path, '*png')):
                name, _ext = os.path.splitext(os.path.basename(sprite))
                animation_name = name if prefix is None else '{}/{}'.format(prefix, name)
                animation = Animation(animation_name, sprite, self._target_image, scale)
                animation.connect('animation-loaded', self._on_animation_loaded)
                self._pending_animations[animation_name] = animation
        return GLib.SOURCE_REMOVE

    def load(self, subpath, prefix=None, scale=1):
        self._loading = True
        self._animation_after_load = None
        self._animations = {}
        GLib.idle_add(self._do_load, subpath, prefix, scale)

    def _on_animation_loaded(self, animation):
        self._animations[animation.name] = animation
        del self._pending_animations[animation.name]

        if not self._pending_animations:
            self._loading = False

        if self._animation_after_load is not None:
            self.play(self._animation_after_load)

    def play(self, name):
        if self._loading:
            self._animation_after_load = name
            return

        new_animation = self._animations.get(name)
        current_animation = self.get_current_animation()

        if new_animation is None:
            logger.debug('Animation \'%s\' not found. Current animation will be cleared.', name)
            AnimationSystem.remove_animation(id(self))
            self._target_image.clear()
            return

        if current_animation is not None and new_animation != current_animation:
            current_animation.reset()

        AnimationSystem.animate(id(self), new_animation)

    def has_animation(self, name):
        return self._animations.get(name) is not None

    def get_animation_scale(self, name):
        animation = self._animations.get(name)
        if animation is not None:
            return animation.scale
        return None

    def get_current_animation(self):
        return AnimationSystem.get_animation(id(self))


class Animation(GObject.GObject):

    __gsignals__ = {
        'animation-loaded': (
            GObject.SignalFlags.RUN_FIRST, None, ()
        ),
    }

    def __init__(self, name, path, target_image, scale=1):
        super().__init__()
        self._loop = True
        self._anchor = (0, 0)
        self._reference_points = {}
        self.name = name
        self.frames = []
        self.last_updated = None
        self.target_image = target_image
        self.reset()
        self.load(path, scale)

    def reset(self):
        self.frame_index = 0

    def advance_frame(self):
        num_frames = len(self.frames)

        # If the animation is not looped, we just don't advance it past the last frame.
        if not self._loop and self.frame_index + 1 == num_frames:
            return

        self.frame_index += 1
        if self.frame_index >= num_frames:
            self.frame_index = 0

        self._set_current_frame_delay()

    def _get_current_frame(self):
        return self.frames[self.frame_index]

    def _set_current_frame_delay(self):
        delay = self.current_frame['delay']
        if not isinstance(delay, str):
            return

        delay_a, delay_b = delay.split('-')
        new_delay = random.randint(int(delay_a), int(delay_b))
        self.current_frame['delay'] = new_delay

    def update_image(self):
        pixbuf = self.current_frame['pixbuf']
        self.target_image.set_from_pixbuf(pixbuf)

    def load(self, sprite_path, scale=1):
        self.scale = scale
        self._reference_points = {}

        file = Gio.File.new_for_path(sprite_path)
        file.read_async(GLib.PRIORITY_DEFAULT, None, self._sprite_file_read_async_cb,
                        sprite_path, scale)

    def _sprite_file_read_async_cb(self, file, result, sprite_path, scale):
        try:
            stream = file.read_finish(result)
            GdkPixbuf.Pixbuf.new_from_stream_async(
                stream, None, self._sprite_pixbuf_read_async_cb, sprite_path, scale)
        except GLib.Error:
            logger.warning("Error: Failed to read file:", sprite_path)

    def _sprite_pixbuf_read_async_cb(self, _stream, result, sprite_path, scale):
        try:
            sprite_pixbuf = GdkPixbuf.Pixbuf.new_from_stream_finish(result)
        except GLib.Error:
            logger.warning("Error: Failed to extract pixel data from file:", sprite_pixbuf)
            return
        self._do_load(sprite_path, sprite_pixbuf, scale)

    def _do_load(self, sprite_path, sprite_pixbuf, scale):
        self._anchor = (0, 0)
        self.frames = []

        metadata = self.get_animation_metadata(sprite_path)
        sprite_width = sprite_pixbuf.get_width()
        width = metadata['width']
        height = metadata['height']

        self._reference_points = metadata.get('reference-points', {})

        subpixbufs = []
        for offset_x in range(0, sprite_width, width):
            pixbuf = GdkPixbuf.Pixbuf.new_subpixbuf(sprite_pixbuf,
                                                    offset_x, 0,
                                                    width, height)
            # Scale final frame if needed
            if scale != 1:
                pixbuf = pixbuf.scale_simple(pixbuf.get_width() * scale,
                                             pixbuf.get_height() * scale,
                                             GdkPixbuf.InterpType.BILINEAR)
            subpixbufs.append(pixbuf)

        if 'frames' in metadata:
            default_delay = metadata.get('default-delay', DEFAULT_DELAY)
            for frame in metadata['frames']:
                frame_index, delay = self._parse_frame(frame, default_delay)
                pixbuf = subpixbufs[frame_index]
                self.frames.append({'pixbuf': pixbuf, 'delay': delay})

        self._loop = metadata.get('loop', True)

        anchor = metadata.get('anchor', (0, 0))
        assert len(anchor) == 2, ('The anchor given by the animation in "%s" does not have'
                                  'two elements: %s', sprite_path, anchor)
        self.anchor = anchor
        self._set_current_frame_delay()
        self.emit('animation-loaded')

    def get_reference_point(self, refpoint_name):
        refpoint = self._reference_points.get(refpoint_name)
        if refpoint is None:
            return None
        return tuple(refpoint)

    current_frame = property(_get_current_frame)

    @staticmethod
    def _convert_delay_to_microseconds(delay):
        if isinstance(delay, str):
            if '-' not in delay:
                return int(delay) * 1000

            delay_a, delay_b = delay.split('-')
            return ('{}-{}'.format(int(delay_a) * 1000, int(delay_b) * 1000))

        return delay * 1000

    @staticmethod
    def _parse_frame(frame, default_delay):
        if isinstance(frame, str):
            frame, delay = frame.split(' ')
            delay = Animation._convert_delay_to_microseconds(delay)
            return int(frame), delay

        delay = Animation._convert_delay_to_microseconds(default_delay)
        return frame, delay

    @staticmethod
    def get_animation_metadata(image_path, load_json=True):
        metadata = None
        image_name, _ext = os.path.splitext(image_path)
        metadata_path = image_name + '.json'
        with open(metadata_path) as f:
            if load_json:
                metadata = json.load(f)
            else:
                metadata = f.read()

        return metadata

    def _get_anchor(self):
        return self._anchor

    def _set_anchor(self, anchor):
        self._anchor = tuple(anchor)

    anchor = GObject.Property(_get_anchor, _set_anchor, type=GObject.TYPE_PYOBJECT)


class AnimationSystem:
    _animations = {}

    @classmethod
    def animate(class_, id_, animation):
        class_._animations[id_] = animation
        animation.update_image()

    @classmethod
    def get_animation(class_, id_):
        return class_._animations.get(id_)

    @classmethod
    def remove_animation(class_, id_):
        if id_ in class_._animations:
            del class_._animations[id_]

    @classmethod
    def step(class_, _widget, clock):
        timestamp = clock.get_frame_time()

        for animation in class_._animations.values():
            if animation.last_updated is None:
                animation.last_updated = timestamp

            elapsed = timestamp - animation.last_updated
            if elapsed >= animation.current_frame['delay']:
                animation.advance_frame()
                animation.update_image()

                animation.last_updated = timestamp

        return GLib.SOURCE_CONTINUE


class Direction(Enum):
    LEFT = -1
    RIGHT = 1
    DOWN = 2
    UP = -2

    def get_opposite(self):
        return Direction(-self.value)
