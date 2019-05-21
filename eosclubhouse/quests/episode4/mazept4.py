from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack


class MazePt4(Quest):

    __available_after_completing_quests__ = ['FizzicsKey']
    __complete_episode__ = True

    def __init__(self):
        super().__init__('MazePt4', 'ada')
        self._app = Sidetrack()
        self.confirmed_messages = []

    def _reset_confirmed_messages(self):
        self.confirmed_messages = []

    def _get_unconfirmed_message(self, message_id_list):
        for message_id in message_id_list:
            if message_id not in self.confirmed_messages:
                return message_id
        return None

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        self._app.set_js_property('willPlayFelixEscapeAnimation', ('b', False))
        self.should_do_runoff = False
        if self._app.get_js_property('highestAchievedLevel') > 40:
            self._app.set_js_property('highestAchievedLevel', ('u', 36))
        self._app.set_js_property('availableLevels', ('u', 40))
        self._reset_confirmed_messages()
        return self.step_play_level, False

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self, level_changed, level_success=None):
        current_level = int(self._app.get_js_property('currentLevel'))
        message_id = None
        if current_level == 36:
            self.show_hints_message('FLIP')
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
            self.show_hints_message('UNITS')
        elif current_level == 37:
            self.dismiss_message()
            message_id = self._get_unconfirmed_message(['LEVELS2'])
        elif current_level == 38:
            message_id = self._get_unconfirmed_message(['LEVELS3'])
        elif current_level == 39:
            message_id = self._get_unconfirmed_message(['LEVELS4', 'LEVELS4_SANIEL'])
        elif current_level == 40:
            message_id = self._get_unconfirmed_message([
                'LEVELS5', 'LEVELS5_RILEY', 'LEVELS5_SANIEL'])
            self._app.set_js_property('willPlayFelixEscapeAnimation', ('b', True))
            self.should_do_runoff = True
        else:
            self.dismiss_message()

        actions = [self.connect_app_js_props_changes(self._app, ['currentLevel',
                                                                 'success',
                                                                 'willPlayFelixEscapeAnimation',
                                                                 'escapeCutscene'])]
        if message_id is not None:
            actions.append(self.show_confirm_message(message_id))

        self.wait_for_one(actions)

        level_changed = False
        level_success = None
        if self.confirmed_step():
            self.confirmed_messages.append(message_id)
        elif self.should_do_runoff and \
                not self._app.get_js_property('willPlayFelixEscapeAnimation'):
            self._app.set_js_property('escapeCutscene', ('b', True))
        elif self.should_do_runoff and not self._app.get_js_property('escapeCutscene'):
            return self.step_final
        elif current_level != self._app.get_js_property('currentLevel'):
            level_changed = True
            self._reset_confirmed_messages()
        else:
            # Current level hasn't changed, so either the player
            # completed the level or died:
            level_success = self._app.get_js_property('success')

        return self.step_play_level, level_changed, level_success

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_final(self):
        self.wait_confirm('END1')
        self.wait_confirm('END2')
        self.wait_confirm('END3')
        self.wait_confirm('END4')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        # Yay riley's back
        self.gss.set('clubhouse.character.Riley', {'in_trap': False})
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
