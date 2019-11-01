from eosclubhouse.libquest import Quest
from eosclubhouse.system import App


class MakerTechDraw(Quest):

    APP_NAME = 'com.hack_computer.ProjectLibrary'
    ARTICLE_NAME = 'Technical Drawing'

    __tags__ = ['pathway:maker']
    __pathway_order__ = 255

    def setup(self):
        self._app = App(self.APP_NAME)

    def step_begin(self):
        self.wait_confirm('WELCOME')
        self._app.open_article(self.ARTICLE_NAME)
        return self.step_complete_and_stop
