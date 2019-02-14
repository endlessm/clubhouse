from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Hackdex2Find(Quest):

    APP_NAME = 'com.endlessm.Hackdex2'

    def __init__(self):
        super().__init__('Hackdex2Find', 'riley')
        self._app = App(self.APP_NAME)

    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.APP_NAME):
                return self.step_explanation
            self.show_hints_message('LAUNCH')
            Desktop.add_app_to_grid(self.APP_NAME)
            Desktop.focus_app(self.APP_NAME)

        if Desktop.app_is_running(self.APP_NAME) or self.debug_skip():
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_question('EXPLANATION', confirm_label='Bye')

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
