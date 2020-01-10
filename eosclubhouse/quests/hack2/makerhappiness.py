from eosclubhouse.libquest import Quest


class MakerHappiness(Quest):

    __app_id__ = 'com.hack_computer.ProjectLibrary'
    ARTICLE_NAME = 'Make your own Happiness'

    __tags__ = ['pathway:maker', 'difficulty:easy', 'since:1.4']
    __pathway_order__ = 250

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOQUEST_PROJLIB_NOTINSTALLED', confirm_label='App Center, got it.')
            return self.step_abort
        else:
            return self.step_instruct

    def step_instruct(self):
        self.wait_confirm('WELCOME', confirm_label='Yeah!')
        if self.is_cancelled():
            return self.step_abort()
        self.app.open_article(self.ARTICLE_NAME)
        return self.step_complete_and_stop
