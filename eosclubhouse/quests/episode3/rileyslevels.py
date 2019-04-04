from eosclubhouse.apps import Fizzics
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class RileysLevels(Quest):

    __available_after_completing_quests__ = ['SetUp']

    FIRST_RILEY_LEVEL = 12
    SECOND_RILEY_LEVEL = FIRST_RILEY_LEVEL + 1
    LAST_RILEY_LEVEL = 16

    def __init__(self):
        super().__init__('RileysLevels', 'ada')
        self._app = Fizzics()

        # These hints are given only once:
        self._hints_given_once = None

    def _show_hints_message_once(self, message):
        if message in self._hints_given_once:
            return
        self.show_hints_message(message)
        self._hints_given_once.add(message)

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
        # Resetting hints here because they should be given once per run:
        self._hints_given_once = set()

        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_explain_reach_previous_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_explain_reach_previous_level(self):
        self.show_hints_message('GETTOLEVEL11')
        return self.step_reach_previous_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_reach_previous_level(self):
        level = self._app.get_current_level(self.debug_skip())
        if level > self.LAST_RILEY_LEVEL:
            return self.step_success, True
        elif level >= self.FIRST_RILEY_LEVEL:
            return self.step_explain_beat_riley_levels
        elif level == self.FIRST_RILEY_LEVEL - 1:
            return self.step_explain_beat_previous_level

        self._wait_for_app_changes()
        return self.step_reach_previous_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_ball_died(self, message, next_step):
        self._show_hints_message_once(message)
        self.wait_for_app_js_props_changed(self._app, ['ballDied'])
        return next_step

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_explain_beat_previous_level(self):
        self.show_hints_message('LEVEL11')
        return self.step_beat_previous_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_beat_previous_level(self):
        level = self._app.get_current_level(self.debug_skip())
        if level > self.LAST_RILEY_LEVEL:
            return self.step_success, True
        elif level >= self.FIRST_RILEY_LEVEL:
            return self.step_explain_beat_riley_levels

        self._wait_for_app_changes()
        return self.step_beat_previous_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_explain_beat_riley_levels(self):
        self.show_hints_message('LEVEL12')
        return self.step_beat_riley_levels

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_beat_riley_levels(self):
        level = self._app.get_current_level(self.debug_skip())
        if level > self.LAST_RILEY_LEVEL:
            return self.step_success

        if self.SECOND_RILEY_LEVEL <= level <= self.LAST_RILEY_LEVEL:
            self._show_hints_message_once('START_LEVEL{}'.format(int(level)))

        change = self._wait_for_app_changes()
        if change == 'levelSuccess' and level == self.LAST_RILEY_LEVEL:
            return self.step_success
        elif change == 'ballDied':
            if level == self.FIRST_RILEY_LEVEL:
                return self.step_ball_died, 'DIED_LEVEL12', self.step_beat_riley_levels
            elif level == self.SECOND_RILEY_LEVEL:
                return self.step_ball_died, 'DIED_LEVEL13', self.step_beat_riley_levels
        return self.step_beat_riley_levels

    def step_success(self, already_beat=False):
        Sound.play('quests/quest-complete')
        msg_id = 'ALREADYBEAT' if already_beat else 'SUCCESS'
        self.wait_confirm(msg_id)
        self.give_item('item.fob.1', consume_after_use=True)

        self.complete = True
        self.available = False
        self.stop()
