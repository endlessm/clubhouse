from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, GameStateService


class System_Tour(Quest):

    APP_NAME = 'com.hack_computer.OperatingSystemApp'

    __tags__ = ['pathway:operating system', 'difficulty:easy', 'skillset:LaunchQuests']
    __pathway_order__ = 100

    def setup(self):
        self._app = App(self.APP_NAME)
        self._gss = GameStateService()

    def step_begin(self):
        self.wait_confirm('GREET1')
        # don't bother with keys, just unlock everything
        for lockNumber in range(1, 4):
            self._gss.set('lock.OperatingSystemApp.' + str(lockNumber), {'locked': False})
        return self.step_launch

    def step_launch(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        return self.step_app_running

    @Quest.with_app_launched(APP_NAME)
    def step_app_running(self):
        self.wait_confirm('STUFFTODO')
        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        self.wait_confirm('FLIPPEDSTUFF')
        return self.step_complete_and_stop(available=False)
