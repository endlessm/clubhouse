import os
from gi.repository import Gtk

from eosclubhouse import config


class BadgeButton(Gtk.Button):
    _WIDTH = 195
    _HEIGHT = 195

    def __init__(self, episode):
        super().__init__(halign=Gtk.Align.START,
                         relief=Gtk.ReliefStyle.NONE)

        self._episode = episode
        self._setup_ui()

        style_context = self.get_style_context()
        style_context.add_class('badge')

    def _setup_ui(self):
        badgename = '{}.png'.format(self._episode.id)
        filename = os.path.join(config.EPISODES_DIR, 'badges', badgename)

        img = Gtk.Image()
        img.set_from_file(filename)
        pixbuf = img.get_pixbuf()
        if pixbuf:
            self._HEIGHT = pixbuf.get_height()
            self._WIDTH = pixbuf.get_width()

        label = Gtk.Label(label=self._episode.name)
        label.set_line_wrap(True)
        label.set_size_request(self._WIDTH, -1)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.add(label)
        vbox.add(img)
        vbox.show_all()

        self.add(vbox)

    def get_size(self):
        return self._WIDTH, self._HEIGHT
