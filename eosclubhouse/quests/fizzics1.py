from eosclubhouse.utils import QS, QSH
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Fizzics1(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics 1', 'riley', QS('FIZZICS1_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._current_step = None
        self.gss.connect('changed', self.update_availability)
        self.already_in_level_8 = False
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("FizzicsIntro"):
            self.available = True

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
            self.already_in_level_8 = False
            if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                self.show_hints_message(QSH('FIZZICS1_LAUNCH'))
                Desktop.focus_app(self.TARGET_APP_DBUS_NAME)
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
            if self.get_current_level() >= 8:
                return self.step_already_beat
            Sound.play('quests/step-forward')
            self.show_hints_message(QSH('FIZZICS1_GOAL'))

        if self.get_current_level() == 7:
            return self.step_level8
        try:
            # Check for popping ball
            if self._app.get_js_property('ballDied'):
                self._current_step = self.step_goal
                return self.step_ball_died
        except Exception as ex:
            print(ex)
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_ball_died(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message(QSH('FIZZICS1_BALLDIED'))
        try:
            # Check for popping ball
            if not self._app.get_js_property('ballDied'):
                return self._current_step
        except Exception as ex:
            print(ex)
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_backtolevel8(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICS1_BACKTOLEVEL8'))

        if self.get_current_level() == 7:
            return self.step_level8
        try:
            # Check for popping ball
            if self._app.get_js_property('ballDied'):
                self._current_step = self.step_backtolevel8
                return self.step_ball_died
        except Exception as ex:
            print(ex)
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_level8(self, time_in_step):
        if time_in_step == 0:
            if self.already_in_level_8:
                self.show_hints_message(QSH('FIZZICS1_LEVEL8AGAIN'))
            else:
                Sound.play('quests/step-forward')
                self.show_hints_message(QSH('FIZZICS1_LEVEL8'))
                self.already_in_level_8 = True

        try:
            # Check for flipping the app
            if self._app.get_js_property('flipped'):
                return self.step_flipped
            # Check for success
            if self.get_current_level() >= 8 or self._app.get_js_property('levelSuccess'):
                return self.step_success
            # Check for popping ball
            if self._app.get_js_property('ballDied'):
                self._current_step = self.step_level8
                return self.step_ball_died
        except Exception as ex:
            print(ex)
        # Check if they're going to another level
        if self.get_current_level() < 7:
            return self.step_backtolevel8
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
            if self.get_current_level() == 8 or self._app.get_js_property('levelSuccess'):
                return self.step_success
        except Exception as ex:
            print(ex)
        # Check for going to another level
        if self.get_current_level() < 7:
            return self.step_backtolevel8
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            self.show_message(QS('FIZZICS1_SUCCESS'), choices=[('Bye', self._confirm_step)])

        if self.confirmed_step():
            self.stop()

    def step_already_beat(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            self.show_message(QS('FIZZICS1_ALREADYBEAT'), choices=[('Bye', self._confirm_step)])

        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message(QS('FIZZICS1_ABORT'))

        if time_in_step > 5:
            self.stop()
