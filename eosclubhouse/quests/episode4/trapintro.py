from eosclubhouse.libquest import Quest
from eosclubhouse.system import GameStateService
# from eosclubhouse.apps import Sidetrack


class TrapIntro(Quest):
    # This quest just goes straight through with no stopping
    def __init__(self):
        super().__init__('TrapIntro', 'trap')
        self._gss = GameStateService()
        # self._app = Sidetrack()

    def step_begin(self):
        # silently install the app
        # self.give_app_icon(_app.dbus_name)
        return self.step_success

    def step_success(self):
        self.show_message('TRAPINTRO_SUCCESS').wait(10)
        # hide the trap
        self._gss.set('clubhouse.character.Trap', {'deployed': True})
        self.complete = True
        self.available = False
        self.stop()
