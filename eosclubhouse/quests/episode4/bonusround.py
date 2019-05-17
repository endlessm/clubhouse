from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack
# from eosclubhouse import logger


class BonusRound(Quest):

    __available_after_completing_quests__ = ['MazePt4']

    def __init__(self):
        super().__init__('BonusRound', 'riley')
        self._app = Sidetrack()
        self.confirmed_messages = []
        self.state_level47 = 'initial'

    def is_unlocked(self):
        lock_state = self.gss.get('lock.sidetrack.3')
        return lock_state is not None and not lock_state.get('locked', True)

    def _reset_confirmed_messages(self):
        self.confirmed_messages = []

    def _get_unconfirmed_message(self, message_id_list):
        for message_id in message_id_list:
            if message_id not in self.confirmed_messages:
                return message_id
        return None

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        if self._app.get_js_property('highestAchievedLevel') < 41:
            self._app.set_js_property('highestAchievedLevel', ('u', 41))
        self._app.set_js_property('availableLevels', ('u', 50))
        self._reset_confirmed_messages()
        self.level50_fliptracker = False
        if self.is_unlocked():
            self.state_level47 = 'unlocked'
        return self.step_play_level, False

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self, level_changed, level_success=None, level_flipped=False):
        current_level = int(self._app.get_js_property('currentLevel'))
        message_id = None
        if current_level == 41:
            message_id = self._get_unconfirmed_message(['LEVELS1'])
            if message_id is None:
                self.show_hints_message('LEVELS1_B')
        elif current_level == 42:
            message_id = self._get_unconfirmed_message(['LEVELS2'])
            if message_id is None:
                self.show_hints_message('LEVELS2_B')
        elif current_level == 43:
            message_id = self._get_unconfirmed_message(['LEVELS3'])
        elif current_level == 44:
            message_id = self._get_unconfirmed_message(['LEVELS4'])
        elif current_level == 45:
            message_id = self._get_unconfirmed_message(['LEVELS5'])
        elif current_level == 46:
            message_id = self._get_unconfirmed_message(['LEVELS6'])
            if message_id is None:
                self.show_hints_message('LEVELS6_B')
        elif current_level == 47:
            # check to see if we're resuming
            if self.is_unlocked():
                self.state_level47 = 'unlocked'
            # intial state
            if self.state_level47 == 'initial':
                self.wait_confirm('LEVELS7')
                self.pause(1)
                self.wait_confirm('LEVELS7_B')
                self.pause(0.5)
                self.give_item('item.key.sidetrack.3')
                self.state_level47 = 'needflip'
            # waiting for the the player to flip
            elif self.state_level47 == 'needflip':
                if level_flipped:
                    self.state_level47 = 'needunlock'
                else:
                    self.wait_confirm('LEVELS7_FLIP')
            # wait to unlock
            elif self.state_level47 == 'needunlock':
                return self.step_level47_lock
            # now the player can complete the level
            elif self.state_level47 == 'unlocked':
                message_id = self._get_unconfirmed_message(['LEVELS7_LEVELCODE1',
                                                            'LEVELS7_LEVELCODE2'])
                if message_id is None:
                    self.show_hints_message('LEVELS7_LEVELCODE3')
        elif current_level == 48:
            self.show_hints_message('LEVELS8')
        elif current_level == 49:
            self.wait_confirm('LEVELS9')
        elif current_level == 50:
            if self.level50_fliptracker:
                return self.step_success
            if level_flipped:
                self.show_hints_message('LEVELS10_B')
                self.level50_fliptracker = True
            else:
                message_id = self._get_unconfirmed_message(['LEVELS10'])
        else:
            self.dismiss_message()

        actions = [self.connect_app_js_props_changes(self._app, ['currentLevel',
                                                                 'success',
                                                                 'flipped'])]
        if message_id is not None:
            actions.append(self.show_confirm_message(message_id))

        self.wait_for_one(actions)

        level_changed = False
        level_success = None
        level_flipped = False
        if self._app.get_js_property('flipped') is True:
            level_flipped = True
        if self.confirmed_step():
            self.confirmed_messages.append(message_id)
        elif current_level != self._app.get_js_property('currentLevel'):
            level_changed = True
            self._reset_confirmed_messages()
        else:
            # Current level hasn't changed, so either the player
            # completed the level or died:
            level_success = self._app.get_js_property('success')

        return self.step_play_level, level_changed, level_success, level_flipped

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_level47_lock(self):
        if self.is_unlocked():
            self.state_level47 = 'unlocked'
            return self.step_play_level, False, False, True
        else:
            self.pause(1)
            return self.step_level47_lock

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
