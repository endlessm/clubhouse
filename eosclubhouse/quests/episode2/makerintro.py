from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class MakerIntro(Quest):

    APP_NAME = 'com.endlessm.Fizzics'
    GAME_PRESET = 1001

    def __init__(self):
        super().__init__('MakerIntro', 'faber')
        self._app = App(self.APP_NAME)
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("Chore"):
            self.available = True

    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.APP_NAME):
                return self.step_explanation
            self.show_hints_message('LAUNCH')
            Desktop.add_app_to_grid(self.APP_NAME)
            Desktop.focus_app(self.APP_NAME)

        if Desktop.app_is_running(self.APP_NAME) or self.debug_skip():
            return self.step_delay

    # Delay to hope that the Clippy interface is ready by the time we're done
    def step_delay(self, time_in_step):
        if time_in_step >= 2:
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('EXPLANATION')
            self._app.set_js_property('preset', ('i', self.GAME_PRESET))

        if self._app.get_js_property('quest1Success') or self.debug_skip():
            return self.step_success
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.show_question('SUCCESS')
        if self.confirmed_step():
            return self.step_whatisit
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_whatisit(self, time_in_step):
        if time_in_step == 0:
            self.show_question('WHATISIT')
        if self.confirmed_step():
            return self.step_anotherone
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_anotherone(self, time_in_step):
        if time_in_step == 0:
            self.show_question('ANOTHERONE')
        if self.confirmed_step():
            return self.step_thanks
        if not Desktop.app_is_running(self.APP_NAME):
            return self.step_abort

    def step_thanks(self, time_in_step):
        if time_in_step == 0:
            self.show_question('THANKS', confirm_label='Bye')
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
