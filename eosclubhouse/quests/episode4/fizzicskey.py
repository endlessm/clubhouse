from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Fizzics
from eosclubhouse import logger


class FizzicsKey(Quest):

    __available_after_completing_quests__ = ['MazePt3']
    PRESET_NUM = 16

    def __init__(self):
        super().__init__('FizzicsKey', 'saniel')
        self._app = Fizzics()

    def reset_params(self):
        # found the defaults
        # self._app.set_js_property('gravity_0', ('u', 0))
        # self._app.set_js_property('friction_0', ('u', 10))
        # self._app.set_js_property('collision_0', ('d', 0.2))
        return

    def set_tools(self):
        # disable adding not-rocks (from T26376-app branch)
        # self._app.disable_add_tool_for_ball_type(0)
        # self._app.disable_add_tool_for_ball_type(1)
        # self._app.disable_add_tool_for_ball_type(2)
        # self._app.disable_add_tool_for_ball_type(4)
        self._app.set_js_property('createType0Disabled', ('b', True))
        self._app.set_js_property('createType1Disabled', ('b', True))
        self._app.set_js_property('createType2Disabled', ('b', True))
        self._app.set_js_property('createType4Disabled', ('b', True))
        # disable tools, this way prevents the visual desync
        self._app.set_js_property('flingToolDisabled', ('b', True))
        self._app.set_js_property('moveToolDisabled', ('b', True))
        self._app.set_js_property('deleteToolDisabled', ('b', True))
        self._app.set_js_property('createToolDisabled', ('b', False))
        # Make tools visible
        self._app.set_js_property('flingToolActive', ('b', False))
        self._app.set_js_property('moveToolActive', ('b', False))
        self._app.set_js_property('deleteToolActive', ('b', False))
        self._app.set_js_property('createToolActive', ('b', True))

    def phys_off(self):
        self._app.set_js_property('usePhysics_0', ('b', False))
        logger.debug("set physics0 OFF-DISABLED (%s)", self._app.get_js_property('usePhysics_0'))

    def phys_on(self):
        self._app.set_js_property('usePhysics_0', ('b', True))
        logger.debug("set physics0 ON-ENABLED (%s)", self._app.get_js_property('usePhysics_0'))

    def do_level1_fric(self, result):
        if result:
            self._app.set_js_property('friction_0', ('u', 5))
        else:
            self._app.set_js_property('friction_0', ('u', 0))

    def do_level1_bounce(self, result):
        if result:
            self._app.set_js_property('collision_0', ('d', 0.1))
        else:
            self._app.set_js_property('collision_0', ('d', 2))

    def do_level2_fric(self, result):
        if result:
            self._app.set_js_property('friction_0', ('u', 5))
        else:
            self._app.set_js_property('friction_0', ('u', 0))

    def do_level2_repulse(self, result):
        if result:
            self._app.set_js_property('socialForce_0_2', ('d', -30))
        else:
            self._app.set_js_property('socialForce_0_2', ('d', 0))

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_ingame

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_ingame(self):
        self._app.set_js_property('preset', ('i', self.PRESET_NUM))
        self.set_tools()
        self.phys_off()
        self._app.set_js_property('gravity_0', ('u', 0))
        self._app.set_js_property('friction_0', ('u', 10))
        self._app.set_js_property('collision_0', ('d', 0.2))
        return self.step_level1_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1_pre(self):
        self.wait_confirm('LEVELS1')
        self.wait_confirm('LEVELS1_B')
        self._app.set_js_property('gravity_0', ('u', 50))
        self.phys_on()
        self.pause(7)
        self.wait_confirm('LEVELS1_C')
        self._app.set_js_property('preset', ('i', self.PRESET_NUM))
        self._app.reset()
        self.pause(0.7)
        self.set_tools()
        self.phys_off()
        return self.step_level1

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1(self):
        self.show_confirm_message('LEVELS1_READY', confirm_label='Ready!').wait()
        self._app.set_js_property('friction_0', ('u', 10))
        self._app.set_js_property('collision_0', ('d', 0.2))

        choiceHigh = ('LEVELS1_Q1_A1', self.do_level1_fric, True)
        choiceLow = ('LEVELS1_Q1_A2', self.do_level1_fric, False)
        self.show_choices_message('LEVELS1_Q1', choiceHigh, choiceLow).wait()

        choiceHigh = ('LEVELS1_Q2_A1', self.do_level1_bounce, True)
        choiceLow = ('LEVELS1_Q2_A2', self.do_level1_bounce, False)
        self.show_choices_message('LEVELS1_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS1_GO')
        cl = int(self._app.get_current_level())
        self.phys_on()
        self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'ballDied'], timeout=15)
        logger.debug("currentLevel changed, ballDied, or time limit occurred")

        if self._app.get_current_level() <= cl:
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.7)
            self.set_tools()
            self.phys_off()
            self.wait_confirm('LEVELS1_FAIL')
            return self.step_level1
        else:
            self.phys_off()
            self.wait_confirm('LEVELS1_FINISH')
            return self.step_level2

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2(self):
        self.show_confirm_message('LEVELS2_READY', confirm_label='Ready!').wait()
        self._app.set_js_property('friction_0', ('u', 10))
        self._app.set_js_property('collision_0', ('d', 0.2))

        choiceHigh = ('LEVELS2_Q1_A1', self.do_level2_repulse, True)
        choiceLow = ('LEVELS2_Q1_A2', self.do_level2_repulse, False)
        self.show_choices_message('LEVELS2_Q1', choiceHigh, choiceLow).wait()

        choiceHigh = ('LEVELS2_Q2_A1', self.do_level2_fric, True)
        choiceLow = ('LEVELS2_Q2_A2', self.do_level2_fric, False)
        self.show_choices_message('LEVELS2_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS2_GO')
        cl = int(self._app.get_current_level())
        self.phys_on()
        self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'ballDied'], timeout=15)
        logger.debug("currentLevel changed, ballDied, or time limit occurred")

        if self._app.get_current_level() <= cl:
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.7)
            self.set_tools()
            self.phys_off()
            self.wait_confirm('LEVELS2_FAIL')
            return self.step_level2
        else:
            self.phys_off()
            self.wait_confirm('LEVELS2_FINISH')
            return self.step_level3

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3(self):
        self.reset_params()

        choiceHigh = ('CHOICEHIGH', self.do_result_bounce, True)
        choiceLow = ('CHOICELOW', self.do_result_bounce, False)
        self.show_choices_message('SETBOUNCE', choiceHigh, choiceLow).wait()

        self._app.set_js_property('usePhysics_0', ('b', True))
        self.wait_confirm('DUMMY3')
        self.reset_params()
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        self.give_item('item.key.sidetrack.2')
        Sound.play('quests/quest-complete')
        self.stop()
