from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App
from gi.repository import Gio, GLib


class BreakSomething(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('Break Something', 'ricky', QS('BREAK_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()
        self.settings = Gio.Settings.new("org.gnome.desktop.interface")
        self._hintIndex = -1
        self._hints = []
        self._hint_character_id = None

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("OSIntro"):
            self.available = True

    def set_hints(self, dialog_id, character_id=None):
        self._hintIndex = -1
        self._hints = [QS(dialog_id)]
        self._hint_character_id = character_id
        hintIndex = 0
        while True:
            hintIndex += 1
            hintId = dialog_id + '_HINT' + str(hintIndex)
            hintStr = QS(hintId)
            if hintStr is None:
                break
            self._hints.append(hintStr)
        self.show_hint()

    def show_hint(self):
        label = 'Hint'
        if self._hintIndex >= len(self._hints) - 1:
            self._hintIndex = 0
        else:
            self._hintIndex += 1
            if self._hintIndex == len(self._hints) - 1:
                label = 'Goal'
        self.show_message(self._hints[self._hintIndex], choices=[(label, self.show_hint)],
                          character_id=self._hint_character_id)

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                return self.step_explanation
            self.set_hints('BREAK_LAUNCH')
            Desktop.show_app_grid()

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_delay1

    def step_delay1(self, time_in_step):
        if time_in_step > 1:
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('BREAK_OSAPP'))
        if self.confirmed_step():
            return self.step_flip
        try:
            if self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                return self.step_givekey
        except Exception as e:
            print(e)
        # Abort if exiting app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_flip(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('BREAK_FLIP')

        try:
            if self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                return self.step_givekey
        except Exception as e:
            print(e)
        # Abort if exiting app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_givekey(self, time_in_step):
        if time_in_step == 0:
            try:
                item = self.gss.get('item.key.OperatingSystemApp.1')
                # If we already have the key, skip this step.
                if item is not None:
                    # If the panel is already unlocked, skip all that
                    if item.get('used', False):
                        return self.step_unlocked
                    # Otherwise prompt player to unlock it
                    else:
                        return self.step_unlock
            except Exception as e:
                print(e)
            self.show_question(QS('BREAK_GIVEKEY'))

        if self.confirmed_step():
            self.give_item('item.key.OperatingSystemApp.1')
            return self.step_unlock
        # Abort if exiting app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_unlock(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('BREAK_UNLOCK')

        item = self.gss.get('item.key.OperatingSystemApp.1')
        if item is not None and item.get('used', False):
            return self.step_unlocked
        # Abort if exiting app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_unlocked(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('BREAK_UNLOCKED'))

        if self.confirmed_step():
            return self.step_makeitlarge
        if self.settings.get_int('cursor-size') >= 200:
            return self.step_success
        # Abort if exiting app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_makeitlarge(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('BREAK_MAKEITLARGE')

        if self.settings.get_int('cursor-size') >= 200:
            return self.step_success
        # Abort if exiting app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('BREAK_SUCCESS'))
        if self.confirmed_step():
            return self.step_archivist

    def step_archivist(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('BREAK_ARCHIVISTARRIVES'), character_id='archivist')
        if self.confirmed_step():
            return self.step_reset

    def step_reset(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('BREAK_GIVERESET', character_id='archivist')
            # Set reset button visible
            variant = GLib.Variant('a{sb}', {'visible': True})
            self.gss.set("app.hack_toolbox.reset_button", variant)

        if self.settings.get_int('cursor-size') == 24:
            return self.step_reward

    def step_reward(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('BREAK_WRAPUP'), character_id='archivist')
            self.conf['complete'] = True
            self.available = False

        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('BREAK_ABORT'))

        if time_in_step > 5:
            self.stop()
