from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class ArtSnapshot(Quest):

    APP_NAME = 'com.hack_computer.ProjectLibrary'
    ARTICLE_NAME = 'Snapshot'

    __tags__ = ['pathway:art', 'difficulty:easy', 'skillset:LaunchQuests']
    __pathway_order__ = 400

    def setup(self):
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if not self._app.is_installed():
            self.wait_confirm('NOQUEST_PROJLIB_NOTINSTALLED', confirm_label='App Center, got it.')
            return self.step_abort
        else:
            return self.step_instruct

    def step_instruct(self):
        self.wait_confirm('WELCOME', confirm_label='Interesting...')
        self._app.open_article(self.ARTICLE_NAME)
        return self.step_complete_and_stop
