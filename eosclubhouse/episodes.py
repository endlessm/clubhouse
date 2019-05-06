import os
from gi.repository import Gdk, Gio, GLib, Gtk

from eosclubhouse import config, libquest, logger, utils
from eosclubhouse.system import Sound


class BadgeButton(Gtk.Button):
    _poster = None

    WIDTH = HEIGHT = 164

    PROGRESS_BADGES = [15, 30, 50, 70, 85]

    def __init__(self, episode):
        super().__init__(halign=Gtk.Align.START,
                         relief=Gtk.ReliefStyle.NONE)

        self._episode = episode
        self._setup_ui()

        style_context = self.get_style_context()
        style_context.add_class('badge')

        self.connect('state-flags-changed', self._style_flags_changed_cb)

        self._update()

        self._episode.connect('notify::percentage-complete',
                              lambda *args: self._update())

    def _style_flags_changed_cb(self, _button, previous_flags):
        # If the prelight flag of the current or previous states differ, then we update the image.
        current_flags = self.get_state_flags()
        if previous_flags & Gtk.StateFlags.PRELIGHT != current_flags & Gtk.StateFlags.PRELIGHT:
            self._update()

    def _setup_ui(self):
        self._image = Gtk.Image()
        self._image.show()
        self.add(self._image)

    def _get_progress_for_percentage(self, percentage):
        if percentage == 0:
            return 0

        step = 100 // len(self.PROGRESS_BADGES)
        progress_index = int(percentage // step)
        return self.PROGRESS_BADGES[progress_index]

    def _update(self):
        percentage_complete = self._episode.percentage_complete
        if percentage_complete == 100:
            if self.get_state_flags() & Gtk.StateFlags.PRELIGHT:
                badgename = '{}_hover.png'.format(self._episode.id)
            else:
                badgename = '{}.png'.format(self._episode.id)
        elif self._episode.is_current:
            progress = self._get_progress_for_percentage(percentage_complete)
            badgename = 'episode_progress_{}.png'.format(progress)
        else:
            self.hide()
            return

        self.show()

        filename = os.path.join(config.EPISODES_DIR, 'badges', badgename)

        self._image.set_from_file(filename)


class PosterWindow(Gtk.Window):
    def __init__(self, episode):
        super().__init__(title=episode.name, skip_taskbar_hint=False,
                         application=Gio.Application.get_default())
        screen = Gdk.Screen.get_default()
        self.set_visual(screen.get_rgba_visual())

        self._episode = episode
        self._next = None
        self._sound_uuid = None

        next_episodes = utils.EpisodesDB().get_next_episodes(episode.id)
        if next_episodes:
            self._next = next_episodes[0]

        self._setup_ui()

    def _setup_ui(self):
        badgename = '{}.png'.format(self._episode.id)
        bgfile = os.path.join(config.EPISODES_DIR, 'backgrounds', badgename)
        badgefile = os.path.join(config.EPISODES_DIR, 'badges', badgename)

        builder = Gtk.Builder()
        builder.add_from_resource('/com/endlessm/Clubhouse/posterwindow.ui')

        self._modal = Gtk.Dialog(flags=Gtk.DialogFlags.DESTROY_WITH_PARENT)

        container = builder.get_object('container')
        title_label = builder.get_object('title')
        subtitle_label = builder.get_object('subtitle')
        bg = builder.get_object('bg_image')
        image = builder.get_object('episode_image')

        bg.set_from_file(bgfile)
        image.set_from_file(badgefile)

        text = "End of episode {} | <b>{}</b>".format(self._episode.number,
                                                      self._episode.name)
        title_label.set_markup(text)

        text = "Episode {} coming soon…".format(self._episode.number + 1)
        if self._next:
            available_episodes = libquest.Registry.get_available_episodes()
            if self._next.id not in available_episodes:
                text = "<i>coming soon ⭑  Episode {} | {}</i>".format(self._next.number,
                                                                      self._next.name)
            else:
                text = ""
        subtitle_label.set_markup(text)

        container.show_all()
        self._modal.get_content_area().add(container)
        self._modal.get_content_area().set_border_width(0)

        self._modal.get_style_context().add_class('poster')
        self.get_style_context().add_class('poster')
        self.set_hide_titlebar_when_maximized(True)
        self.set_keep_above(True)

        self._modal.set_title('')
        self._modal.set_resizable(False)
        self._modal.set_transient_for(self)
        self._modal.set_attached_to(self)
        self._modal.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self._modal.set_modal(False)
        self._modal.set_destroy_with_parent(True)
        self._modal.set_position(Gtk.WindowPosition.CENTER)

        # We have to call maximize before setting the GdkWindow functions in the
        # realize callback, otherwise the size of the window will not change.
        self.maximize()
        self._modal.connect('realize', self._window_realized_cb)
        self._modal.connect('delete-event', self._hide)

        self.connect('delete-event', self._hide)
        self.connect('show', self._show)
        self.connect('realize', self._window_realized_cb)

    def _window_realized_cb(self, window):
        gdk_window = window.get_window()
        gdk_window.set_functions(Gdk.WMFunction.CLOSE)

    def _hide(self, _widget, _event):
        self._modal.hide()
        self.hide()

        if self._sound_uuid == 'pending':
            self._sound_uuid = 'cancel'
        elif self._sound_uuid:
            Sound.stop(self._sound_uuid)
            self._sound_uuid = None

        return True

    def _show(self, _window):
        self._modal.present()
        self.set_keep_above(True)

        if self._sound_uuid == 'pending':
            return

        if self._sound_uuid == 'cancel':
            self._sound_uuid = 'pending'
            return

        self._sound_uuid = 'pending'
        Sound.play('clubhouse/ending/%s' % self._episode.id,
                   result_handler=self._sound_playing)

    def _sound_playing(self, _proxy, result, user_data=None):
        if isinstance(result, GLib.GError):
            self._sound_uuid = None
            logger.error('Can not play the poster sound "%s": %s',
                         self._episode.id, result)
            return

        if self._sound_uuid == 'cancel':
            Sound.stop(result)
            self._sound_uuid = None
            return

        self._sound_uuid = result
