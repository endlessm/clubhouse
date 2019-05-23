from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, ToolBoxTopic
from eosclubhouse.apps import LightSpeed


class LightspeedKey(Quest):

    __available_after_completing_quests__ = ['MazePt1']

    FIRST_LEVEL = 15
    LAST_LEVEL = 17

    # Maps the toolbox panels to the labels used in message IDs:
    MESSAGES_FOR_PANELS = {
        'game': 'GAME',
        'spawn': 'SPAWN',
        'updateAsteroid': 'ASTEROID',
        'updateSpinner': 'SPINNER',
        'updateSquid': 'SQUID',
        'updateBeam': 'BEAM',
        'activatePowerup': 'POWERUPS',
    }

    def __init__(self):
        super().__init__('LightspeedKey', 'faber')
        self._app = LightSpeed()

    def step_begin(self):
        self.all_messages = [
            'LAUNCH',
            'LEVELSINTRO',
            'LEVELS1',
            'LEVELS2',
            'LEVELS3',
            'PANEL_LOCKED',
            'PANEL_GAME',
            'PANEL_SPAWN',
            'PANEL_ASTEROID',
            'PANEL_SPINNER',
            'PANEL_SQUID',
            'PANEL_BEAM',
            'PANEL_POWERUPS',
            'SUCCESS',
            'ABORT',
        ]
        return self.step_test

    def step_test(self):
        try:
            message_id = self.all_messages.pop()
            print(message_id)
            self.show_hints_message(message_id)
            self.pause(15)
            return self.step_test
        except IndexError:
            return self.step_success

    def step_success(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
