from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class SanielQuest1(Quest):

    APP_NAME = 'com.endlessm.Sidetrack'

    def __init__(self):
        super().__init__('SanielQuest1', 'saniel')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_main

    @Quest.with_app_launched(APP_NAME)
    def step_main(self):
        self.wait_confirm('INITIALTEXT')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
