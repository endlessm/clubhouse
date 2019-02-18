from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Investigation(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('Investigation', 'riley')
        self._app = App(self.APP_NAME)
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("MakerIntro"):
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
            return self.step_flip

    def step_flip(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('FLIP')
        if self.debug_skip():
            return self.step_unlock

    def step_unlock(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('UNLOCK')
        if self.debug_skip():
            return self.step_stop

    def step_stop(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('STOP')
        if self.debug_skip():
            return self.step_end

    def step_end(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.show_question('END', confirm_label='Bye')
            Sound.play('quests/quest-complete')
        if self.confirmed_step():
            self.stop()

    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message('ABORT')

        if time_in_step > 5:
            self.stop()
