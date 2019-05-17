from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack


class MazePt2(Quest):

    __available_after_completing_quests__ = ['LightspeedKey']

    def __init__(self):
        super().__init__('MazePt2', 'ada')
        self._app = Sidetrack()
        self.confirmed_messages = []
        self.unlocked = False
        self.postHackdex = False

    def _reset_confirmed_messages(self):
        self.confirmed_messages = []

    def _get_unconfirmed_message(self, message_id_list):
        for message_id in message_id_list:
            if message_id not in self.confirmed_messages:
                return message_id
        return None

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_wait_for_unlock(self):
        if self.is_panel_unlocked('lock.sidetrack.1'):
            self.unlocked = True
            return self.step_play_level, False, False
        else:
            self.pause(1)
            return self.step_wait_for_unlock

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        highest_level = self._app.get_js_property('highestAchievedLevel')
        if highest_level < 27:
            self._app.set_js_property('showHackdex', ('b', True))
        else:
            self._app.set_js_property('showHackdex', ('b', False))
        if highest_level < 23 or highest_level > 28:
            self._app.set_js_property('highestAchievedLevel', ('u', 23))
        self._app.set_js_property('availableLevels', ('u', 28))
        if self.is_panel_unlocked('lock.sidetrack.1'):
            self.unlocked = True
        self._reset_confirmed_messages()
        return self.step_play_level, False

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self, level_changed, level_success=None):
        current_level = int(self._app.get_js_property('currentLevel'))
        message_id = None
        if current_level == 23:
            if not self.unlocked:
                self.show_hints_message('FLIP')
                return self.step_wait_for_unlock
            else:
                self.pause(4)
                self.show_hints_message('INSTRUCTIONS')
        elif current_level == 24:
            message_id = self._get_unconfirmed_message(['LEVELS2'])
            if message_id is None:
                self.show_hints_message('LEVELS2_B')
        elif current_level == 25:
            message_id = self._get_unconfirmed_message(['FIXANDREORDER'])
        elif current_level == 26:
            if self._app.get_js_property('showHackdex'):
                self.postHackdex = True
                message_id = self._get_unconfirmed_message(['LEVELS5', 'LEVELS5_RILEY'])
        elif current_level == 27:
            if self.postHackdex:
                self.postHackdex = False
                message_id = self._get_unconfirmed_message(['RESEARCH1', 'RESEARCH2'])
            else:
                self.dismiss_message()
        elif current_level == 28:
            for message_id in ['IMPASSABLE', 'IMPASSABLE_FABER', 'IMPASSABLE_RILEY']:
                self.wait_confirm(message_id)
            return self.step_success
        else:
            self.dismiss_message()

        actions = [self.connect_app_js_props_changes(self._app, ['currentLevel', 'success'])]
        if message_id is not None:
            actions.append(self.show_confirm_message(message_id))

        self.wait_for_one(actions)

        level_changed = False
        level_success = None
        if self.confirmed_step():
            self.confirmed_messages.append(message_id)
        elif current_level != self._app.get_js_property('currentLevel'):
            level_changed = True
            self._reset_confirmed_messages()
        else:
            # Current level hasn't changed, so either the player
            # completed the level or died:
            level_success = self._app.get_js_property('success')

        return self.step_play_level, level_changed, level_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
