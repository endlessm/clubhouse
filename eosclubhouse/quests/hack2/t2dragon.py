from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class T2Dragon(Quest):

    APP_NAME = 'com.endlessnetwork.dragonsapprentice'

    __quest_name__ = '''Terminal 2 - Dragon's Apprentice'''
    __tags__ = ['mission:ada', 'pathway:games', 'difficulty:normal']
    __mission_order__ = 126
    __pathway_order__ = 126

    def setup(self):
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if not self._app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='App Center, got it.')
            return self.step_abort
        else:
            self.wait_confirm('GREET1')
            self.wait_confirm('GREET2', confirm_label="I'll remember that...")
            return self.step_launch

    def step_launch(self):
        self._app.launch()
        return self.step_complete_and_stop
