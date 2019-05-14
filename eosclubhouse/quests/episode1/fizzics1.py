from eosclubhouse.apps import Fizzics
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Fizzics1(Quest):

    __available_after_completing_quests__ = ['FizzicsIntro']

    def __init__(self):
        super().__init__('Fizzics 1', 'riley')
        self._app = Fizzics()
        self.already_in_level_8 = False

    def _app_is_flipped(self):
        return bool(self._app.get_js_property('flipped'))

    def get_current_level(self):
        return self._app.get_effective_level(self.debug_skip())

    def step_begin(self):
        self.already_in_level_8 = False
        self.ask_for_app_launch(self._app)
        return self.step_goal

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_goal(self):
        Sound.play('quests/step-forward')
        self.show_hints_message('GOAL')
        return self.step_check_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_check_level(self):
        level = self.get_current_level()
        # Check to see if the goal is already beat
        if level >= 9:
            return self.step_success, True

        if level == 8:
            return self.step_level8

        # Check for level change
        level_action = self.connect_app_props_changes(self._app, ['effectiveLevel'])
        # Check for popping ball
        balldied_action = self.connect_app_js_props_changes(self._app, ['ballDied'])

        self.wait_for_one([level_action, balldied_action])

        if self._app.get_js_property('ballDied'):
            return self.step_ball_died, self.step_goal

        return self.step_check_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_ball_died(self, next_step):
        self.show_hints_message('BALLDIED')
        self.wait_for_app_js_props_changed(self._app, ['ballDied'])
        return next_step

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level8(self):
        if self._app_is_flipped():
            return self.step_flipped

        level = self.get_current_level()
        if level == 8:
            if self.already_in_level_8:
                self.show_hints_message('LEVEL8AGAIN')
            else:
                Sound.play('quests/step-forward')
                self.show_hints_message('LEVEL8')
                self.already_in_level_8 = True
        elif level >= 9:
            return self.step_success
        else:
            self.show_message('BACKTOLEVEL8')

        # Check for level change
        level_action = self.connect_app_js_props_changes(self._app, ['currentLevel', 'levelSuccess',
                                                                     'flipped'])
        # Check for popping ball
        balldied_action = self.connect_app_js_props_changes(self._app, ['ballDied'])

        self.wait_for_one([level_action, balldied_action])

        if self._app.get_js_property('ballDied'):
            return self.step_ball_died, self.step_level8

        return self.step_level8

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_flipped(self):
        Sound.play('quests/step-forward')
        self.show_hints_message('FLIPPED')
        return self.step_check_unlocked

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_check_unlocked(self):
        if not self._app_is_flipped():
            return self.step_level8

        # Wait until they unlock the panel
        item = self.gss.get('item.key.fizzics.1')
        if item is not None and item.get('used', False):
            return self.step_hack

        flipped_action = self.connect_app_js_props_changes(self._app, ['flipped'])

        # Wait for the flip state or the GSS properties to change
        self.wait_for_one([self.connect_gss_changes(), flipped_action])

        return self.step_check_unlocked

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_hack(self):
        level = self.get_current_level()
        if level == 9:
            return self.step_success

        if level < 8:
            self.show_message('BACKTOLEVEL8')
        else:
            Sound.play('quests/step-forward')
            self.show_hints_message('HACK')

        self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'levelSuccess'])
        return self.step_hack

    def step_success(self, already_beat=False):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        msg_id = 'ALREADYBEAT' if already_beat else 'SUCCESS'
        self.show_message(msg_id, choices=[('Bye', self.stop)])
