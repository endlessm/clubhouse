import unittest

from eosclubhouse.system import GameStateService
from gi.repository import Gio, GObject


class _GSSMockProxy(GObject.GObject):

    __state__ = {}

    __gsignals__ = {
        'g-signal': (
            GObject.SignalFlags.RUN_FIRST, None, (str, str, GObject.TYPE_VARIANT)
        ),
    }

    def call(self, method_name, variant, _flags, _timeout, _param, done_callback):
        method = getattr(self, method_name)

        method(variant.format_string, variant.get_child_value(0), variant.get_child_value(1))

        done_callback(self, None)

    def Get(self, _variant_format, key):
        try:
            return self.__state__[key]
        except KeyError:
            raise Gio.DBusError.new_for_dbus_error("com.endlessm.GameStateService.KeyError",
                                                   "Phony KeyError")

    def Set(self, _variant_format, key, variant):
        self.__state__[key] = variant.unpack()
        self.emit('g-signal', 'phony', 'changed', None)

    def Reset(self):
        self.__state__ = {}

    def call_finish(self, _param):
        pass


class ClubhouseTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Ensure the GSS doesn't affect the real game state.
        GameStateService._proxy = _GSSMockProxy()

        # Reset the GSS so every test case starts with a clean slate.
        cls.reset_gss()

    @classmethod
    def reset_gss(self):
        GameStateService().reset()
