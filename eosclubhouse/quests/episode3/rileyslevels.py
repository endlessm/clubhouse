from eosclubhouse.apps import Fizzics
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class RileysLevels(Quest):

    __available_after_completing_quests__ = ['SetUp']
    __items_on_completion__ = {'item.fob.1': {'consume_after_use': True}}

    FIRST_RILEY_LEVEL = 12
    SECOND_RILEY_LEVEL = FIRST_RILEY_LEVEL + 1
    LAST_RILEY_LEVEL = 16

    def setup(self):
        self._app = Fizzics()

    def _wait_for_app_changes(self):
        app_changes = self.connect_app_js_props_changes(self._app,
                                                        ['currentLevel', 'levelSuccess',
                                                         'ballDied'])
        app_changes.wait()

        if self._app.get_js_property('ballDied', False):
            return 'ballDied'
        elif self._app.get_js_property('levelSuccess', False):
            return 'levelSuccess'
        return 'currentLevel'

    def step_begin(self):
        self._already_beat = True
        self._previous_msg_id = None
        self.ask_for_app_launch(self._app)
        return self.step_check_previous_levels

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_check_previous_levels(self):
        level = self._app.get_current_level(self.debug_skip())

        if level > self.LAST_RILEY_LEVEL:
            return self.step_success

        self._already_beat = False

        message_id = None

        if level >= self.FIRST_RILEY_LEVEL:
            self._previous_msg_id = 'LEVEL12'
            self.show_hints_message(self._previous_msg_id)
            return self.step_beat_riley_levels

        if level == self.FIRST_RILEY_LEVEL - 1:
            message_id = 'LEVEL11'
            # This level should be impossible until this quest runs:
            self._app.disable_tool('create', disabled=False)
        elif level < self.FIRST_RILEY_LEVEL - 1:
            message_id = 'GETTOLEVEL11'

        if self._previous_msg_id == message_id:
            message_id = None
        else:
            self._previous_msg_id = message_id

        if message_id is not None:
            self.show_hints_message(message_id)

        self._wait_for_app_changes()
        return self.step_check_previous_levels

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_ball_died(self, message):
        self.show_hints_message(message, give_once=True)
        self.wait_for_app_js_props_changed(self._app, ['ballDied'])
        # Give time for the currentLevel to change if it's the case.
        self.pause(.250)
        return self.step_check_previous_levels

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_beat_riley_levels(self):
        level = self._app.get_current_level(self.debug_skip())
        if level > self.LAST_RILEY_LEVEL:
            return self.step_success

        if self.SECOND_RILEY_LEVEL <= level <= self.LAST_RILEY_LEVEL:
            self.show_hints_message('START_LEVEL{}'.format(int(level)), give_once=True)

        change = self._wait_for_app_changes()

        if change == 'currentLevel' and \
           self._app.get_current_level(self.debug_skip()) < self.SECOND_RILEY_LEVEL:
            return self.step_check_previous_levels
        if change == 'levelSuccess' and level == self.LAST_RILEY_LEVEL:
            return self.step_success
        elif change == 'ballDied':
            if level == self.FIRST_RILEY_LEVEL:
                return self.step_ball_died, 'DIED_LEVEL12'
            elif level == self.SECOND_RILEY_LEVEL:
                return self.step_ball_died, 'DIED_LEVEL13'
        return self.step_beat_riley_levels

    def step_success(self):
        Sound.play('quests/quest-complete')
        msg_id = 'ALREADYBEAT' if self._already_beat else 'SUCCESS'
        self.wait_confirm(msg_id)
        self.give_item('item.fob.1', consume_after_use=True)

        self.complete = True
        self.available = False
        self.stop()
