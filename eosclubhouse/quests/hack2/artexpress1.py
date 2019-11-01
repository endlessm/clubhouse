from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class ArtExpress1(Quest):

    APP_NAME = 'com.hack_computer.ProjectLibrary'
    ARTICLE_NAME = "Express Yourself (Part 1 of 2)"

    __tags__ = ['pathway:art']
    __pathway_order__ = 405

    def setup(self):
        self._app = App(self.APP_NAME)

    def step_begin(self):
        self.wait_confirm('WELCOME')
        self._app.open_article(self.ARTICLE_NAME)
        return self.step_complete_and_stop
