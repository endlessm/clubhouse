from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GLib


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
                         default_width=200,
                         default_height=230)

        self.set_visual(self.get_screen().get_rgba_visual())
        self.set_keep_above(True)

        self._css_provider = Gtk.CssProvider()
        self._css_provider.load_from_data("\
        @keyframes pulsate {\
            from { opacity: 0.9; background-size: 100%; }\
            to   { opacity: 0.5; background-size: 92%;  }\
        }\
        window.splash {\
            opacity: 0.9;\
            background-color: unset;\
            background-image: url('/app/share/eos-clubhouse/splash.svg');\
            background-size: cover;\
            background-position: center;\
            background-repeat: no-repeat;\
            animation: pulsate 500ms ease-in-out infinite alternate;\
        }\
        window.splash.fadeout {\
            opacity: 0;\
        }".encode())
        ctx = self.get_style_context()
        ctx.add_class('splash')
        ctx.add_provider_for_screen(self.get_screen(), self._css_provider,
                                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def destroy_with_fadeout(self):
        self.get_style_context().add_class('fadeout')
        GLib.timeout_add(1000, self._destroy_timeout)

    def _destroy_timeout(self):
        ctx = self.get_style_context()
        ctx.remove_provider_for_screen(self.get_screen(), self._css_provider)
        self.destroy()
        return GLib.SOURCE_REMOVE
