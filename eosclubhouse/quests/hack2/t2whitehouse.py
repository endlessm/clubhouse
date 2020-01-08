from eosclubhouse.libquest import Quest


class T2Whitehouse(Quest):

    __app_id__ = 'com.endlessnetwork.whitehouse'
    __tags__ = ['pathway:games', 'difficulty:normal', 'since:1.4']
    __pathway_order__ = 130

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOTINSTALLED', confirm_label='App Center, got it.')
            return self.step_abort
        return self.step_instruct

    def step_instruct(self):
        self.wait_confirm('GREET1')
        self.wait_confirm('GREET2', confirm_label='Interesting!')
        return self.step_launch

    def step_launch(self):
        self.app.launch()
        self.wait_for_app_in_foreground()
        self.wait_for_app_in_foreground(in_foreground=False)
        return self.step_complete_and_stop
