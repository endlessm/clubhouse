from eosclubhouse.libquest import Quest


class ArtVerb(Quest):

    __app_id__ = 'com.hack_computer.ProjectLibrary'
    ARTICLE_NAME = 'Verb In A Hat'

    __tags__ = ['pathway:art', 'difficulty:easy', 'skillset:LaunchQuests']
    __pathway_order__ = 415

    def step_begin(self):
        if not self.app.is_installed():
            self.wait_confirm('NOQUEST_PROJLIB_NOTINSTALLED', confirm_label='App Center, got it.')
            return self.step_abort
        else:
            return self.step_instruct

    def step_instruct(self):
        self.wait_confirm('WELCOME', confirm_label="I'll try it!")
        self.app.open_article(self.ARTICLE_NAME)
        return self.step_complete_and_stop
