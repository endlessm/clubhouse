from eosclubhouse.libquest import Quest
from eosclubhouse.system import GameStateService
from eosclubhouse.apps import Sidetrack


class TrapIntro(Quest):

    __conf_on_completion__ = {'clubhouse.character.Trap': {'deployed': True}}

    # This quest just goes straight through with no stopping
    def setup(self):
        self._gss = GameStateService()
        self._app = Sidetrack()

    def step_begin(self):
        # silently install the app
        self.give_app_icon(self._app.dbus_name)
        self.wait_confirm('QUESTION_ACCEPT')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        # hide the trap (must wait until quest ends)
        self._gss.set('clubhouse.character.Trap', {'deployed': True})
        self.stop()
