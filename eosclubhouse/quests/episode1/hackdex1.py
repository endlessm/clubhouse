from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class HackdexCorruption(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Hackdex_chapter_one'

    def __init__(self):
        super().__init__('Hackdex Corruption', 'saniel', QS('HACKDEX1_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("BreakSomething") and \
           self.is_named_quest_complete("Roster"):
            self.available = True

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.gss.set('app.com_endlessm_Hackdex_chapter_one.corruption',
                         {'state': 'corrupted', 'color': ''})
            self.show_question('HACKDEX1_PRELAUNCH')
        if self.confirmed_step():
            return self.step_launch

    def step_launch(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('HACKDEX1_LAUNCH')
            Desktop.focus_app(self.TARGET_APP_DBUS_NAME)

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_delay1

    def step_delay1(self, time_in_step):
        if time_in_step > 2:
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message('HACKDEX1_GOAL')

        # Check unlock level 1
        item = self.gss.get('item.key.hackdex1.1')
        if item is not None and item.get('used', False):
            return self.step_check_goal

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_check_goal(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_hints_message('HACKDEX1_UNLOCKED')

        # Check for color change
        data = self.gss.get('app.com_endlessm_Hackdex_chapter_one.corruption')
        if data is None:
            return self.step_abort

        if data['state'] == 'fixed' or self.debug_skip():
            return self.step_delay2

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_check_abort

    def step_delay2(self, time_in_step):
        if time_in_step > 2:
            return self.step_success

    def step_success(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_message('HACKDEX1_SUCCESS', choices=[('OK', self._confirm_step)])

        if self.confirmed_step():
            return self.step_afterkey

    def step_afterkey(self, time_in_step):
        if time_in_step == 0:
            self.give_item('item.key.fizzics.2')
            self.show_question('HACKDEX1_AFTERKEY')
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')

        if self.confirmed_step():
            self.stop()

    def step_check_abort(self, time_in_step):
        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_check_goal
        if time_in_step > 2:
            return self.step_abort

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message('HACKDEX1_ABORT')

        if time_in_step > 5:
            self.stop()
