from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class BreakingIn(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('BreakingIn', 'riley')
        self._app = App(self.APP_NAME)
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("MakeDevice"):
            self.available = True

    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.APP_NAME):
                return self.step_explanation
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)

        if Desktop.app_is_running(self.APP_NAME) or self.debug_skip():
            return self.step_delay

    def step_delay(self, time_in_step):
        if time_in_step >= 2:
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('EXPLAIN')
        if self.debug_skip():
            return self.step_flipped
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_flipped(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('FLIPPED')
        if self.debug_skip():
            return self.step_unlocked
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_unlocked(self, time_in_step):
        if time_in_step == 0:
            self.show_question('UNLOCKED')
        if self.confirmed_step():
            return self.step_archivist

    def step_archivist(self, time_in_step):
        if time_in_step == 0:
            self.show_question('ARCHIVIST', confirm_label='End of Episode 2')
        if self.confirmed_step():
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            self.stop()

    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message('ABORT')

        if time_in_step > 5:
            self.stop()
