from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class FizzicsIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Intro', 'ada', QS('FIZZICSINTRO_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)

    def get_current_level(self):
        try:
            level = self._app.get_js_property('currentLevel')
            return level
        except Exception as ex:
            print(ex)
        return -1

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                return self.step_explanation
            self.show_hints_message('FIZZICSINTRO_LAUNCH')
            Sound.play('quests/new-icon')
            Desktop.add_app_to_grid(self.TARGET_APP_DBUS_NAME)
            Desktop.focus_app(self.TARGET_APP_DBUS_NAME)

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_delay_until_ready

    # Wait until the app is up and running
    def step_delay_until_ready(self, time_in_step):
        if self.get_current_level() >= 0:
            return self.step_delay1

    # And now give it 1 more second to initialize its current level
    # That way we can check at the beginning of the next step and not print multiple messages
    def step_delay1(self, time_in_step):
        if time_in_step >= 1:
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            if self.get_current_level() >= 2:
                return self.step_already_beat
            self.show_question('FIZZICSINTRO_EXPLANATION')

        if self.confirmed_step():
            return self.step_level1
        if self.get_current_level() >= 1:
            return self.step_level2
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_level1(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('FIZZICSINTRO_LEVEL1')

        if self.get_current_level() >= 1:
            return self.step_level2
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_level2(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message('FIZZICSINTRO_LEVEL2')

        current_level = self.get_current_level()
        if current_level >= 2 or \
           (current_level == 1 and self._app.get_js_property('levelSuccess')):
            return self.step_success
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.show_question('FIZZICSINTRO_SUCCESS')
        if self.confirmed_step():
            return self.step_prekey

    def step_already_beat(self, time_in_step):
        if time_in_step == 0:
            self.show_question('FIZZICSINTRO_ALREADYBEAT')
        if self.confirmed_step():
            return self.step_prekey

    def step_prekey(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/riley-intro')
            self.show_message('FIZZICSINTRO_KEY', choices=[('OK', self._confirm_step)])
        if self.confirmed_step():
            return self.step_key

    def step_key(self, time_in_step):
        if time_in_step == 0:
            self.give_item('item.key.fizzics.1')
            self.show_question('FIZZICSINTRO_KEYAFTER')
        if self.confirmed_step():
            return self.step_riley

    def step_riley(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/riley-intro')
            self.show_question('FIZZICSINTRO_RILEY')
        if self.confirmed_step():
            return self.step_end

    def step_end(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.show_message('FIZZICSINTRO_END', choices=[('Bye', self._confirm_step)])
            Sound.play('quests/quest-complete')
        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message('FIZZICSINTRO_ABORT')

        if time_in_step > 5:
            self.stop()
