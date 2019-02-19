from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class Hackdex2Find(Quest):

    APP_NAME = 'com.endlessm.Hackdex2'

    def __init__(self):
        super().__init__('Hackdex2Find', 'riley')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        return self.step_explanation

    # @todo: Set as needing the app to be running (we cannot add it yet since the app doesn't exist)
    def step_explanation(self):
        self.show_confirm_message('EXPLANATION', confirm_label='Bye').wait()

        if self.confirmed_step():
            Sound.play('quests/quest-complete')
            self.conf['complete'] = True
            self.available = False

        self.stop()
