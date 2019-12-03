from eosclubhouse.libquest import Quest


class T2Tank(Quest):

    __app_id__ = 'com.endlessnetwork.tankwarriors'
    __tags__ = ['pathway:games', 'difficulty:normal', 'skillset:LaunchQuests']
    __pathway_order__ = 128

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='App Center, got it.')
            return self.step_abort
        else:
            self.app.launch()
            return self.step_instruct

    def step_instruct(self):
        self.wait_confirm('GREET1')
        self.wait_confirm('GREET2', confirm_label='Smart!')
        return self.step_complete_and_stop
