from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound, GameStateService


class System_Tour(Quest):

    APP_NAME = 'com.hack_computer.OperatingSystemApp'

    __quest_name__ = 'Touring the System'
    __tags__ = ['mission:estelle', 'pathway:operating system', 'difficulty:easy']
    __mission_order__ = 100
    __pathway_order__ = 100

    def setup(self):
        self._app = App(self.APP_NAME)
        # we still need to use the GSS as locks aren't handled in conf
        self._gss = GameStateService()

    def step_begin(self):
        self.wait_confirm('GREET1')
        self.wait_confirm('GIVEPERMS')
        # don't bother with keys - we don't even have the inventory anymore, just unlock everything
        for lockNumber in range(1, 4):
            self._gss.set('lock.OperatingSystemApp.' + str(lockNumber), {'locked': False})
        self.show_message('GREET2', choices=[("Let's rock and roll!", self.step_launch)])

    def step_launch(self):
        Sound.play('quests/quest-complete')
        self._app.launch()
        self.wait_for_app_launch(self._app, pause_after_launch=3)
        self.show_message('STUFFTODO', timeout=120, choices=[("Sounds good!", self.step_end)])
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
