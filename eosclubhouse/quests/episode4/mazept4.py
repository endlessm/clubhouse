from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, GameStateService
from eosclubhouse.apps import Sidetrack


class MazePt4(Quest):

    __available_after_completing_quests__ = ['FizzicsKey']
    __complete_episode__ = True

    def __init__(self):
        super().__init__('MazePt4', 'ada')
        self._gss = GameStateService()
        self._app = Sidetrack()

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        self.pause(7)
        self.show_hints_message('INSTRUCTIONS')
        self.pause(7)
        self.wait_confirm('LEVELS2')
        self.wait_confirm('LEVELS3')
        self.wait_confirm('LEVELS4')
        self.wait_confirm('INSTRUCTIONS1')
        self.wait_confirm('SANIELRETURNS')
        self.wait_confirm('SANIELRETURNS2')
        self.wait_confirm('RILEYESCAPE')
        self.wait_confirm('RILEYESCAPE2')
        self.wait_confirm('RILEYESCAPE3')
        self.wait_confirm('RILEYESCAPE4')
        self.wait_confirm('RILEYESCAPE5')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        # Yay riley's back
        self._gss.set('clubhouse.character.Riley', {'in_trap': False})
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
