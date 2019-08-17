from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class T2Intro(Quest):

    APP_NAME = 'com.endlessnetwork.frogsquash'

    __quest_name__ = 'Terminal 2 - FrogSquash'
    __tags__ = ['mission:saniel', 'pathway:games', 'difficulty:easy']
    __mission_order__ = 125
    __pathway_order__ = 125
    __auto_offer_info__ = {'confirm_before': True}

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
        self.wait_confirm('GREET1')
        self.wait_confirm('GREET2', confirm_label='Will do!')
        return self.step_launch

    def step_launch(self):
        self.wait_confirm('BYE')
        self._app.launch()
        return self.step_complete_and_stop
