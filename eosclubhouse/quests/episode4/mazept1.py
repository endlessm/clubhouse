from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack


class MazePt1(Quest):

    __available_after_completing_quests__ = ['TrapIntro']

    def __init__(self):
        super().__init__('MazePt1', 'ada')
        self._app = Sidetrack()
        self.confirmed_messages = []
        self.cutscene_played = False

    def _reset_confirmed_messages(self):
        self.confirmed_messages = []

    def _get_unconfirmed_message(self, message_id_list):
        for message_id in message_id_list:
            if message_id not in self.confirmed_messages:
                return message_id
        return None

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH_ADA')
        self._app.set_js_property('availableLevels', ('u', 23))
        self._reset_confirmed_messages()
        self.cutscene_played = False
        return self.step_play_level, False

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self, level_changed, level_succeed=None):
        current_level = self._app.get_js_property('currentLevel')
        message_id = None
        # messages_to_confirm = []
        # hint_message = None
        if current_level == 1:
            if level_succeed is False:
                message_id = self._get_unconfirmed_message(['DIED_RESTART'])
            else:
                message_id = self._get_unconfirmed_message(['RILEYHELLO', 'EXIT'])
                if message_id is None:
                    self.show_hints_message('MANUAL1')
        elif current_level == 2:
            message_id = self._get_unconfirmed_message(['MANUAL2'])
        elif current_level == 3:
            message_id = self._get_unconfirmed_message(['MANUAL3'])
        elif current_level == 4:
            self.show_hints_message('MANUAL4')
        elif current_level == 6:
            self.show_hints_message('MANUAL5')
        elif current_level == 7:
            message_id = self._get_unconfirmed_message(['ROBOTS1', 'ROBOTS2'])
            if message_id is None:
                self.show_hints_message('ROBOTS3')
        elif current_level == 10:
            message_id = self._get_unconfirmed_message(['MOREROBOTS'])
        elif current_level == 14:
            if not self.cutscene_played:
                self.wait_confirm('AUTO1')
                # felix destroys the controls here
                self._app.set_js_property('controlsCutscene', ('b', True))
                self.pause(1)
                self.wait_for_app_js_props_changed(self._app, ['controlsCutscene'])
                self.cutscene_played = True
            message_id = self._get_unconfirmed_message([
                'AUTO1_FELIX', 'AUTO1_FABER',
                'AUTO1_ADA', 'AUTO1_RILEY',
            ])
            if message_id is None:
                self.show_hints_message('AUTO1_SANIEL')
        elif current_level == 15:
            self.show_hints_message('AUTO2')
        elif current_level == 16:
            if level_changed:
                self.show_hints_message('AUTO3')
            elif level_succeed is True:
                message_id = self._get_unconfirmed_message(['AUTO3_SUCCESS'])
            elif level_succeed is False:
                message_id = self._get_unconfirmed_message(['AUTO3_FAILURE'])
        elif current_level == 17:
            message_id = self._get_unconfirmed_message([
                'AUTO4_BACKSTORY',
                *('AUTO4_BACKSTORY{}'.format(i) for i in range(2, 11)),
            ])
        elif current_level == 18:
            message_id = self._get_unconfirmed_message(['ONEJUMP'])
            if message_id is None:
                self.show_hints_message('ONEJUMP_ADA')
        elif current_level == 19:
            message_id = self._get_unconfirmed_message(['ONEFORWARD'])
            if message_id is None:
                self.show_hints_message('ONEFORWARD_ADA')
        elif current_level == 20:
            message_id = self._get_unconfirmed_message(['SLIDING'])
        elif current_level == 21:
            message_id = self._get_unconfirmed_message(['WASTEJUMPS'])
        elif current_level == 22:
            message_id = self._get_unconfirmed_message([
                'DRAMA_ADA1', 'DRAMA_FABER1', 'DRAMA_ADA2',
                'DRAMA_FABER2', 'DRAMA_ADA3',
            ])
        elif current_level == 23:
            return self.last_level
        else:
            self.dismiss_message()

        actions = [self.connect_app_js_props_changes(self._app, ['currentLevel', 'success'])]
        if message_id is not None:
            actions.append(self.show_confirm_message(message_id))

        self.wait_for_one(actions)

        confirmed = False
        level_changed = False
        next_level_succeed = None
        if self.confirmed_step():
            confirmed = True
            self.confirmed_messages.append(message_id)
        elif current_level != self._app.get_js_property('currentLevel'):
            level_changed = True
            self._reset_confirmed_messages()
        else:
            # Current level hasn't changed, so either the player
            # completed the level or died:
            success = self._app.get_js_property('success')
            # After the player dies the 'success' flag is put back
            # to True, ignore it:
            if level_succeed is not False:
                next_level_succeed = success
            else:
                print('FALSE ALARM')

        print('DEBUG %s %s %s' % (confirmed, level_changed, next_level_succeed))
        return self.step_play_level, level_changed, next_level_succeed

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def last_level(self):
        self.wait_confirm('AUTO5')
        self.show_hints_message('AUTO5_ADA')
        # wait for the player to die, as they cannot pass this level
        self.wait_for_app_js_props_changed(self._app, ['success'])
        self.wait_confirm('AUTO5_FAILURE_ADA')
        self.wait_confirm('AUTO5_FAILURE_ADA2')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
