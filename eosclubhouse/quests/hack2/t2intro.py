from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class T2Intro(Quest):

    APP_NAME = 'com.endlessnetwork.frogsquash'

    __tags__ = ['pathway:games', 'difficulty:easy', 'skillset:LaunchQuests']
    __pathway_order__ = 125

    def setup(self):
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if not self._app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='App Center, got it.')
            return self.step_abort
        else:
            return self.step_check_intro

    def step_check_intro(self):
        if self.get_named_quest_conf('T2Intro', 'has_seen_intro'):
            return self.step_normalrun
        else:
            return self.step_firstrun

    def step_firstrun(self):
        self.wait_confirm('FIRSTRUN1')
        self.wait_confirm('FIRSTRUN2')
        self.set_conf('has_seen_intro', True)
        self.save_conf()
        self.wait_confirm('FIRSTRUN3', confirm_label='OK, got it.')
        return self.step_normalrun

    def step_normalrun(self):
        self._app.launch()
        return self.step_instruct

    def step_instruct(self):
        self.wait_confirm('GREET1')
        self.wait_confirm('GREET2', confirm_label='Will do!')
        self.wait_confirm('BYE')
        return self.step_complete_and_stop
