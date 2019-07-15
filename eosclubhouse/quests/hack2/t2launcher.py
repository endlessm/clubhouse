from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class T2Launcher(Quest):

    # @todo: Replace with the T2 app when it's available.
    APP_NAME = 'com.endlessnetwork.aqueducts'

    __quest_name__ = 'T2 Games'
    __tags__ = ['mission:ada', 'pathway:games']
    __mission_order__ = 90
    __pathway_order__ = 90

    def setup(self):
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if not self._app.is_installed():
            return self.step_install

        self.wait_confirm('BEGIN')
        self.show_message('END', choices=[('Bye', self.step_launch)])

    def step_install(self):
        self.show_message('INSTALL', choices=[('Bye', self.stop)])

    def step_launch(self):
        Sound.play('quests/quest-complete')
        # We are about to launch a fullscreen app. So no messages
        # should be displayed after this point:
        self._app.launch()
        self.wait_for_app_launch(self._app, pause_after_launch=3)
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
