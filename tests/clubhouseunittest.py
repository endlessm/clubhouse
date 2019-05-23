import copy
import unittest

from eosclubhouse.libquest import Registry
from eosclubhouse.system import GameStateService
from eosclubhouse.utils import QuestStringCatalog
from gi.repository import Gio, GObject
from unittest import mock

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

        # We patch the QuestStringCatalog so any changes made by a test aren't kept in the string
        # catalog for the next test or beyond tests. We patch the catalog with a deep copy of it
        # since otherwise only the dictionary is "protected" but not its members (so if a test
        # changes a message's sound, it'd remain like that even with the mock patch).
        strings_catalog_copy = copy.deepcopy(QuestStringCatalog._csv_dict)
        mock.patch.dict('eosclubhouse.utils.QuestStringCatalog._csv_dict',
                        strings_catalog_copy, clear=True).start()

    @classmethod
    def tearDownClass(cls):
        # Stop any mock patches created in the setUpClass.
        mock.patch.stopall()

    @classmethod
    def reset_gss(self):
        GameStateService().reset()


def test_on_episodes(episodes=[]):
    def func_wrapper(function):
        def wrapper(*args, **kwargs):
            _episodes = episodes or Registry.get_available_episodes()

            for episode in _episodes:
                # Load the next episode.
                Registry.set_current_episode(episode)
                Registry.load_current_episode()

                try:
                    # Call the test method.
                    function(*args, **kwargs)
                except Exception:
                    # Inform about which episode failed and propagate the failure.
                    print('Failed test in episode "{}"'.format(episode))
                    raise
        return wrapper

    return func_wrapper


def test_all_episodes(func):
    return test_on_episodes([])(func)
