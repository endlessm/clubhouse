from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Fizzics1(Quest):

    APP_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics 1', 'riley')
        self._app = App(self.APP_NAME)
        self.gss.connect('changed', self.update_availability)
        self.already_in_level_8 = False
        self.available = False
        self.update_availability()

    def _app_is_flipped(self):
        return bool(self._app.get_js_property('flipped'))

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("FizzicsIntro"):
            self.available = True

    def get_current_level(self):
        if self.debug_skip():
            self._level += 1
            return self._level

        success = False
        level = self._app.get_js_property('currentLevel')

        if level is None:
            level = -1
        else:
            success = self._app.get_js_property('levelSuccess')

        self._level = level

        if self._level != -1 and (success or self.debug_skip()):
            self._level += 1

        return self._level

    def step_begin(self):
        self.already_in_level_8 = False
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            Desktop.focus_app(self.APP_NAME)
            self.wait_for_app_launch(self._app)

        self.pause(2)
        return self.step_goal

    def step_abort(self):
        Sound.play('quests/quest-aborted')
        self.show_message('ABORT')

        self.pause(5)
        self.stop()

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_goal(self):
        level = self.get_current_level()
        # Check to see if the goal is already beat
        if level >= 8:
            return self.step_success, True

        Sound.play('quests/step-forward')
        self.show_hints_message('GOAL')

        if level == 7:
            return self.step_level8

        # Check for level change
        level_action = self.connect_app_js_props_changes(self._app,
                                                         ['currentLevel', 'levelSuccess'])
        # Check for popping ball
        balldied_action = self.connect_app_js_props_changes(self._app, ['ballDied'])

        self.wait_for_one([level_action, balldied_action])

        if self._app.get_js_property('ballDied'):
            return self.step_ball_died, self.step_goal

        return self.step_goal

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_ball_died(self, next_step):
        self.show_hints_message('BALLDIED')
        self.wait_for_app_js_props_changed(self._app, ['ballDied'])
        return next_step

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_level8(self):
        if self._app_is_flipped():
            return self.step_flipped

        level = self.get_current_level()
        if level == 7:
            if self.already_in_level_8:
                self.show_hints_message('LEVEL8AGAIN')
            else:
                Sound.play('quests/step-forward')
                self.show_hints_message('LEVEL8')
                self.already_in_level_8 = True
        elif level >= 8:
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

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_flipped(self):
        Sound.play('quests/step-forward')
        self.show_hints_message('FLIPPED')
        return self.step_check_unlocked

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
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

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_hack(self):
        level = self.get_current_level()
        if level == 8:
            return self.step_success

        if level < 7:
            self.show_message('BACKTOLEVEL8')
        else:
            Sound.play('quests/step-forward')
            self.show_hints_message('HACK')

        self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'levelSuccess'])
        return self.step_hack

    def step_success(self, already_beat=False):
        self.conf['complete'] = True
        self.available = False
        Sound.play('quests/quest-complete')
        msg_id = 'ALREADYBEAT' if already_beat else 'SUCCESS'
        self.show_message(msg_id, choices=[('Bye', self.stop)])
