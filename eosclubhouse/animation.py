import glob
import json
import os

from gi.repository import GLib, Gtk, GObject, GdkPixbuf


class AnimationImage(Gtk.Image):
    def __init__(self, path):
        super().__init__()
        self._animations = {}
        self.load(path)

    def load(self, path):
        for sprite in glob.glob(os.path.join(path, '*png')):
            name, _ext = os.path.splitext(os.path.basename(sprite))
            animation = Animation(sprite, self)
            self._animations[name] = animation

    def play(self, name):
        AnimationSystem.animate(id(self), self._animations[name])


class Animation(GObject.GObject):
    def __init__(self, path, target_image):
        super().__init__()
        self.frames = []
        self.frame_index = 0
        self.last_updated = None
        self.target_image = target_image
        self.load(path)

    def advance_frame(self):
        # The animations play in loop for now
        self.frame_index += 1
        if self.frame_index >= len(self.frames):
            self.frame_index = 0

    def _get_current_frame(self):
        return self.frames[self.frame_index]

    def update_image(self):
        pixbuf = self.current_frame['pixbuf']
        self.target_image.set_from_pixbuf(pixbuf)

    def load(self, sprite_path):
        metadata = None
        metadata_path = sprite_path.replace('.png', '.json')
        with open(metadata_path) as f:
            metadata = json.load(f)

        sprite_pixbuf = GdkPixbuf.Pixbuf.new_from_file(sprite_path)

        offset_x = 0
        for delay in metadata['delays']:
            pixbuf = GdkPixbuf.Pixbuf.new_subpixbuf(sprite_pixbuf,
                                                    offset_x, 0,
                                                    metadata['width'],
                                                    metadata['height'])

            # GTK needs the delay in microseconds:
            self.frames.append({'pixbuf': pixbuf, 'delay': delay * 1000})
            offset_x += metadata['width']

    current_frame = property(_get_current_frame)


class AnimationSystem:
    _per_character_animations = {}
    _current_animations = _per_character_animations.values()

    @classmethod
    def animate(class_, character_id, animation):
        class_._per_character_animations[character_id] = animation
        animation.update_image()

    @classmethod
    def step(class_, _widget, clock):
        timestamp = clock.get_frame_time()

        for animation in class_._current_animations:
            if animation.last_updated is None:
                animation.last_updated = timestamp

            elapsed = timestamp - animation.last_updated

            if elapsed >= animation.current_frame['delay']:
                animation.advance_frame()
                animation.update_image()

                animation.last_updated = timestamp

        return GLib.SOURCE_CONTINUE
