from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class T2Whitehouse(Quest):

    APP_NAME = 'com.endlessnetwork.whitehouse'

    __tags__ = ['pathway:games', 'difficulty:normal']
    __pathway_order__ = 130

    def setup(self):
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if not self._app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='App Center, got it.')
            return self.step_abort
        else:
            self._app.launch()
            return self.step_instruct

    def step_instruct(self):
        self.wait_confirm('GREET1')
        self.wait_confirm('GREET2', confirm_label='Sounds cool!')
        return self.step_complete_and_stop
