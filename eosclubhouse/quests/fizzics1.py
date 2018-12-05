from eosclubhouse.utils import QS, QSH
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Fizzics1(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics 1', 'riley', QS('FIZZICS1_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
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
                self.show_hints_message(QSH('FIZZICS1_LAUNCH'))
                Desktop.show_app_grid()
            else:
                return self.step_delay1

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_delay1

    def step_delay1(self, time_in_step):
        if time_in_step > 2:
            return self.step_goal

    def step_goal(self, time_in_step):
        if time_in_step == 0:
            # Check to see if the goal is already beat
            try:
                if self._app.get_js_property('currentLevel') >= 8:
                    return self.step_already_beat
            except Exception as ex:
                print(ex)
            Sound.play('quests/step-forward')
            self.show_hints_message(QSH('FIZZICS1_GOAL'))

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

        try:
            if self._app.get_js_property('currentLevel') == 7:
                return self.step_level8
        except Exception as ex:
            print(ex)

    def step_backtolevel8(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICS1_BACKTOLEVEL8'))

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        try:
            if self._app.get_js_property('currentLevel') == 7:
                return self.step_level8
        except Exception as ex:
            print(ex)

    def step_level8(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message(QSH('FIZZICS1_LEVEL8'))

        try:
            # Check for flipping the app
            if self._app.get_js_property('flipped'):
                return self.step_flipped
            # Check if they're going to another level
            if self._app.get_js_property('currentLevel') != 7:
                return self.step_backtolevel8
            # Check for success
            if self._app.get_js_property('currentLevel') >= 8 or \
               self._app.get_js_property('levelSuccess'):
                return self.step_success
            if self._app.get_js_property('currentLevel') < 7:
                return self.step_backtolevel8
        except Exception as ex:
            print(ex)

        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_flipped(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message(QSH('FIZZICS1_FLIPPED'))

        # Wait until they unlock the panel
        item = self.gss.get('item.key.fizzics.1')
        if item is not None and item.get('used', False):
            return self.step_hack
        # Check for flipping back
        if not self._app.get_js_property('flipped'):
            return self.step_level8

        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_hack(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message(QSH('FIZZICS1_HACK'))

        try:
            # Check for success
            if self._app.get_js_property('currentLevel') == 8 or \
               self._app.get_js_property('levelSuccess'):
                return self.step_success
            # Check for going to another level
            if self._app.get_js_property('currentLevel') < 7:
                return self.step_backtolevel8
        except Exception as ex:
            print(ex)
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            self.show_question(QS('FIZZICS1_SUCCESS'))

        if self.confirmed_step():
            self.stop()

    def step_already_beat(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            self.show_question(QS('FIZZICS1_ALREADYBEAT'))

        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message(QS('FIZZICS1_ABORT'))

        if time_in_step > 5:
            self.stop()
