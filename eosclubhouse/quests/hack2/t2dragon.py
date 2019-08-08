from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class T2Dragon(Quest):

    APP_NAME = 'com.endlessnetwork.dragonsapprentice'

    __quest_name__ = '''Terminal 2 - Dragon's Apprentice'''
    __tags__ = ['mission:saniel', 'pathway:games', 'difficulty:normal']
    __mission_order__ = 126
    __pathway_order__ = 126

    def setup(self):
        self._app = App(self.APP_NAME)

    def step_begin(self):
        self.wait_confirm('GREET1')
        self.show_message('GREET2', choices=[('Cool!', self.step_launch)])

    def step_launch(self):
        Sound.play('quests/quest-complete')
        # We are about to launch a fullscreen app. So no messages
        # should be displayed after this point:
        self._app.launch()
        self.wait_for_app_launch(self._app, pause_after_launch=3)
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
