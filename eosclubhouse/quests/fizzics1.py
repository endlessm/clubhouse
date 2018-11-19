from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App


class Fizzics1(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'
    APP_JS_PARAMS = 'view.JSContext.globalParameters'

    def __init__(self):
        super().__init__('Fizzics 1', 'ricky', QS('FIZZICS1_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._hint0 = False
        self._hint1 = False
        self._hintCount = False
        self._initialized = False
        self._msg = ""
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("FizzicsIntro"):
            self.available = True

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                self.show_message(QS('FIZZICS1_LAUNCH'))
                Desktop.show_app_grid()
            else:
                return self.step_alreadyrunning

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_delay1

        if time_in_step > 20 and not self._hint0:
            self.show_message(QS('FIZZICS1_LAUNCHHINT'))
            self._hint0 = True

    def step_delay1(self, time_in_step):
        if time_in_step > 2:
            return self.step_goal

    def step_alreadyrunning(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICS1_ALREADY_RUNNING'))

        if self.confirmed_step():
            return self.step_goal

    def step_goal(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICS1_GOAL'))

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

        try:
            if self._app.get_object_property(self.APP_JS_PARAMS,
                                             'currentLevel') == 7:
                return self.step_level8
        except Exception as ex:
            print(ex)

    def step_level8(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICS1_LEVEL8'))

        try:
            if self._app.get_object_property(self.APP_JS_PARAMS, 'flipped'):
                return self.step_flipped
            if time_in_step > 20 and not self._hint1:
                self._msg = QS('FIZZICS1_HINT')
                self.show_message(self._msg)
                self._hint1 = True
        except Exception as ex:
            print(ex)

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_flipped(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICS1_FLIPPED'))

        # Wait until they unlock the panel
        item = self.gss.get('item.key.fizzics.1')
        if item is not None and item.get('used', False):
            return self.step_hack

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_hack(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICS1_HACK'))

        try:
            if self._app.get_object_property(self.APP_JS_PARAMS, 'currentLevel') == 8 or \
               self._app.get_object_property(self.APP_JS_PARAMS, 'levelSuccess'):
                return self.step_success
        except Exception as ex:
            print(ex)

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICS1_SUCCESS'))

        if self.confirmed_step():
            return self.step_prereward

    def step_prereward(self, time_in_step):
        if time_in_step == 0:
            if self.is_named_quest_complete("OSIntro"):
                msg = 'FIZZICS1_KEY_ALREADY_OS'
            else:
                msg = 'FIZZICS1_KEY_NO_OS'
            self.show_question(QS(msg))

        if self.confirmed_step():
            return self.step_reward

    # STEP 4
    def step_reward(self, time_in_step):
        if time_in_step == 0:
            self.give_item('item.key.OperatingSystemApp.1')
            self.show_question(QS('FIZZICS1_GIVE_KEY2'))
            self.conf['complete'] = True
            self.available = False

        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICS1_ABORT'))

        if time_in_step > 5:
            self.stop()
