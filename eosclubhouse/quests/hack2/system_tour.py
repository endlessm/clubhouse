from eosclubhouse.libquest import Quest
from eosclubhouse.system import GameStateService


class System_Tour(Quest):

    __app_id__ = 'com.hack_computer.OperatingSystemApp'
    __tags__ = ['pathway:operating system', 'difficulty:easy', 'skillset:LaunchQuests']
    __pathway_order__ = 100

    def setup(self):
        self._gss = GameStateService()

    def step_begin(self):
        self.wait_confirm('GREET1')
        # don't bother with keys, just unlock everything
        for lockNumber in range(1, 4):
            self._gss.set('lock.OperatingSystemApp.' + str(lockNumber), {'locked': False})
        return self.step_launch

    def step_launch(self):
        self.ask_for_app_launch()
        return self.step_app_running

    @Quest.with_app_launched()
    def step_app_running(self):
        self.wait_confirm('STUFFTODO')
        self.wait_for_app_js_props_changed(props=['flipped'])
        self.wait_confirm('FLIPPEDSTUFF')
        return self.step_complete_and_stop
