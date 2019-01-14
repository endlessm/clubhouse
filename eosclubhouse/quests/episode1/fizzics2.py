from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Fizzics2(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics 2', 'riley', QS('FIZZICS2_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._initialized = False

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self._initialized = False
            if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                self.show_hints_message('FIZZICS2_LAUNCH')
                Desktop.focus_app(self.TARGET_APP_DBUS_NAME)
            else:
                return self.step_alreadyrunning

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_delay1

    def step_delay1(self, time_in_step):
        if time_in_step > 2:
            return self.step_set_level

    def step_alreadyrunning(self, time_in_step):
        if time_in_step == 0:
            self.show_question('FIZZICS2_ALREADY_RUNNING')

        if self.confirmed_step():
            return self.step_set_level

    def step_set_level(self, time_in_step):
        try:
            if not self._initialized:
                self._app.set_js_property('preset', ('i', 1000))
                self._initialized = True
        except Exception as ex:
            print(ex)

        if self._initialized:
            return self.step_goal

    def step_goal(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message('FIZZICS2_GOAL')

        try:
            if self._app.get_js_property('quest0Success'):
                return self.step_success
        except Exception as ex:
            print(ex)
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.show_question('FIZZICS2_SUCCESS')

        if self.confirmed_step():
            return self.step_reward

    def step_reward(self, time_in_step):
        if time_in_step == 0:
            self.show_question('FIZZICS2_REWARD')
        if self.confirmed_step():
            return self.step_end

    def step_end(self, time_in_step):
        if time_in_step == 0:
            self.show_question('FIZZICS2_END')
            self.conf['complete'] = True
            self.available = False
            self.give_item('item.key.hackdex1.1')
            Sound.play('quests/quest-complete')

        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message('FIZZICS2_ABORT')

        if time_in_step > 5:
            self.stop()
