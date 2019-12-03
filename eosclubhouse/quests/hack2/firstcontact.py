from gi.repository import Gdk
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop
from eosclubhouse.utils import ClubhouseState


class FirstContact(Quest):

    __app_id__ = 'com.hack_computer.HackUnlock'
    __tags__ = ['pathway:games']
    __dismissible_messages__ = False

    def setup(self):
        # This will prevent the quest from ever being shown in the Clubhouse
        # because it should just be run directly (not by the user)
        self.available = False
        self.skippable = True

    def _is_app_flipped(self):
        if not self.app.is_running():
            return False
        return self.app.get_js_property('mode', default_value=0) >= 1

    def _is_app_hacked(self):
        if not self.app.is_running():
            return False
        return self.app.get_js_property('mode', default_value=0) >= 2

    def _is_app_flipped_back(self):
        if not self.app.is_running():
            return False
        return self.app.get_js_property('mode', default_value=0) >= 4

    def step_begin(self):
        Desktop.set_hack_mode(True, avoid_signal=True)
        self.app.launch()

        # Avoid spinning cursor.
        Gdk.notify_startup_complete()

        self.wait_for_app_launch(pause_after_launch=3)

        if self._is_app_flipped():
            return self.step_wait_for_hack

        return self.step_wait_and_pulse

    @Quest.with_app_launched()
    def step_wait_and_pulse(self):
        self.app.pulse_flip_to_hack_button(True)

        return self.step_wait_for_flip

    @Quest.with_app_launched()
    def step_wait_for_flip(self):
        for hint_msg_id in ['WELCOME', 'WELCOME_HINT1']:
            if self._is_app_flipped() or self.is_cancelled():
                break
            self.wait_for_app_js_props_changed(props=['mode'], timeout=10)
            if not self._is_app_flipped():
                self.show_message(hint_msg_id)

        while not self._is_app_flipped() and not self.is_cancelled():
            self.wait_for_app_js_props_changed(props=['mode'])

        self.app.pulse_flip_to_hack_button(False)
        return self.step_wait_for_hack

    @Quest.with_app_launched()
    def step_wait_for_hack(self):
        self.show_message('GOAL')

        for hint_msg_id in ['GOAL_HINT1', 'GOAL_HINT2']:
            if self._is_app_hacked() or self.is_cancelled():
                break
            self.wait_for_app_js_props_changed(props=['mode'], timeout=30)
            if not self._is_app_hacked():
                self.set_conf('puzzle_hint_given', True)
                self.save_conf()
                self.show_message(hint_msg_id)

        while not self._is_app_hacked() and not self.is_cancelled():
            self.wait_for_app_js_props_changed(props=['mode'])

        self.app.pulse_flip_to_hack_button(True)
        return self.step_wait_for_flipback

    @Quest.with_app_launched()
    def step_wait_for_flipback(self):
        self.show_message('FLIPBACK_HINT1')

        while not self._is_app_flipped_back() and not self.is_cancelled():
            self.wait_for_app_js_props_changed(props=['mode'])

        self.dismiss_message()
        self.app.pulse_flip_to_hack_button(False)
        return self.step_wait_for_finish

    def step_wait_for_finish(self):
        Desktop.set_hack_background(True)
        self.connect_app_quit().wait()
        return self.enter_hack_mode

    def enter_hack_mode(self):
        Desktop.minimize_all()
        Desktop.set_hack_cursor(True)
        return self.step_show_clubhouse

    def step_show_clubhouse(self):
        self.pause(3)

        # hack mode to true to emit the signal and ensure that the clubhouse is ON
        Desktop.set_hack_mode(True)
        # show the clubhouse after the first contact quest
        clubhouse_state = ClubhouseState()
        clubhouse_state.window_is_visible = True
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
        self.stop()

    def step_abort(self):
        Desktop.set_hack_mode(False, avoid_signal=True)
        super().step_abort()
