from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack


class MazePt3(Quest):

    def __init__(self):
        super().__init__('MazePt3', 'ada')
        self._app = Sidetrack()
        self.confirmed_messages = []
        self.level36_hasfailed = False

    def _reset_confirmed_messages(self):
        self.confirmed_messages = []

    def _get_unconfirmed_message(self, message_id_list):
        for message_id in message_id_list:
            if message_id not in self.confirmed_messages:
                return message_id
        return None

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        if self._app.get_js_property('highestAchievedLevel') > 36:
            self._app.set_js_property('highestAchievedLevel', ('u', 28))
        self._app.set_js_property('availableLevels', ('u', 36))
        self._reset_confirmed_messages()
        return self.step_play_level, False

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self, level_changed, level_success=None):
        current_level = self._app.get_js_property('currentLevel')
        message_id = None
        if current_level == 28:
            self.show_hints_message('RILEYPUSH')
            return self.step_level28, False, False, False
        elif current_level == 29:
            self.dismiss_message()
            self.show_hints_message('RILEYPUSH3_B')
        elif current_level == 30:
            self.dismiss_message()
            message_id = self._get_unconfirmed_message(['RILEYPUSH3_C_PUSHINTRO'])
            if message_id is None:
                self.show_hints_message('RILEYPUSH3_C')
        elif current_level == 31:
            self.dismiss_message()
            message_id = self._get_unconfirmed_message([
                *('RILEYPUSH{}'.format(i) for i in range(4, 10))])
        elif current_level == 34:
            self.dismiss_message()
            message_id = self._get_unconfirmed_message(['DRAMA', 'DRAMA_FELIX',
                                                        'DRAMA_FABER', 'DRAMA_RILEY',
                                                        'DRAMA_ADA'])
        elif current_level == 36:
            return self.step_lastlevel
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

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_level28(self, level28_changed, level28_success, level28_flipped):
        if level28_changed:  # or level28_success:
            return self.step_play_level, level28_changed, level28_success
        if level28_flipped:
            self.show_hints_message('RILEYPUSH2')

        level28_actions = [self.connect_app_js_props_changes(self._app, ['currentLevel',
                                                                         'success', 'flipped'])]
        self.wait_for_one(level28_actions)
        level28_changed = False
        level28_success = None
        level28_flipped = False
        if self._app.get_js_property('currentLevel') != 28:
            level28_changed = True
        else:
            # Current level hasn't changed, so either the player
            # completed the level or died:
            level28_success = self._app.get_js_property('success')
        if self._app.get_js_property('flipped'):
            level28_flipped = True
        return self.step_level28, level28_changed, level28_success, level28_flipped

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_lastlevel(self):
        for msg_id in ['FELIXINTRO', 'FELIXINTRO1', 'FELIXINTRO2', 'FELIXINTRO3']:
            self.wait_confirm(msg_id)
        self.wait_for_app_js_props_changed(self._app, ['success'])
        self.wait_confirm('FELIXINTRO_FAILURE')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
