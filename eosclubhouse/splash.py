import os

from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GLib

from eosclubhouse.animation import AnimationImage


# Show spinning icon while loading splash.
Gtk.Window.set_auto_startup_notification(False)


class SplashWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app,
                         type=Gtk.WindowType.TOPLEVEL,
                         type_hint=Gdk.WindowTypeHint.SPLASHSCREEN,
                         decorated=False,
                         skip_pager_hint=True,
                         skip_taskbar_hint=True,
                         default_width=400,
                         default_height=300)

        self.set_visual(self.get_screen().get_rgba_visual())
        self.set_keep_above(True)

        self._css_provider = Gtk.CssProvider()
        self._css_provider.load_from_data("""
        window.splash {
            background-color: unset;
            background-size: cover;
            transition: opacity 1s ease-in-out;
        }
        window.splash.fadeout {
            opacity: 0;
        }
        """.encode())
        ctx = self.get_style_context()
        ctx.add_class('splash')
        ctx.add_provider_for_screen(self.get_screen(), self._css_provider,
                                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        path = os.path.join('splash', 'loading')
        self._loading = AnimationImage(path)
        self._loading.load()
        self._loading.show()
        self.add(self._loading)

        self._loading.play('default')

    def destroy_with_fadeout(self):
        self.get_style_context().add_class('fadeout')
        GLib.timeout_add(1000, self._destroy_timeout)

    def _destroy_timeout(self):
        ctx = self.get_style_context()
        ctx.remove_provider_for_screen(self.get_screen(), self._css_provider)
        self.destroy()
        return GLib.SOURCE_REMOVE
