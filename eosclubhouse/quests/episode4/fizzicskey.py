from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Fizzics
from eosclubhouse import logger


class FizzicsKey(Quest):

    __available_after_completing_quests__ = ['MazePt3']
    PRESET_NUM_BASE = 16

    def __init__(self):
        super().__init__('FizzicsKey', 'saniel')
        self._app = Fizzics()

    # # # # # # # # # # #
    # # UTILITY FXNS  # #
    # # # # # # # # # # #

    def reset_params(self):
        # found the defaults
        self._app.set_js_property('gravity_0', ('i', 0))
        self._app.set_js_property('friction_0', ('i', 10))
        self._app.set_js_property('collision_0', ('d', 0.2))
        return

    def set_tools(self):
        # disable adding not-rocks (from T26376-app branch)
        # self._app.set_js_property('createType0Disabled', ('b', True))
        # self._app.set_js_property('createType1Disabled', ('b', True))
        # self._app.set_js_property('createType2Disabled', ('b', True))
        # self._app.set_js_property('createType4Disabled', ('b', True))
        self._app.disable_tool('fling')
        self._app.disable_tool('delete')
        self._app.disable_tool('move')
        # disable tools, this way prevents the visual desync
        # self._app.set_js_property('flingToolDisabled', ('b', True))
        # self._app.set_js_property('moveToolDisabled', ('b', True))
        # self._app.set_js_property('deleteToolDisabled', ('b', True))
        # self._app.set_js_property('createToolDisabled', ('b', False))
        # Make tools visible
        self._app.set_js_property('flingToolActive', ('b', False))
        self._app.set_js_property('moveToolActive', ('b', False))
        self._app.set_js_property('deleteToolActive', ('b', False))
        self._app.set_js_property('createToolActive', ('b', True))
        self._app.disable_add_tool_for_ball_type(0)
        self._app.disable_add_tool_for_ball_type(1)
        self._app.disable_add_tool_for_ball_type(2)
        self._app.disable_add_tool_for_ball_type(4)

    def phys_off(self):
        self._app.set_js_property('usePhysics_0', ('b', False))
        logger.debug("set physics0 OFF-DISABLED (%s)", self._app.get_js_property('usePhysics_0'))

    def phys_on(self):
        self._app.set_js_property('usePhysics_0', ('b', True))
        logger.debug("set physics0 ON-ENABLED (%s)", self._app.get_js_property('usePhysics_0'))

    # # # # # # # # # # # # #
    # # QUESTION RESULTS  # #
    # # # # # # # # # # # # #

    def do_level1_fric(self, result):
        if result:
            self._app.set_js_property('friction_0', ('i', 5))
        else:
            self._app.set_js_property('friction_0', ('i', 0))

    def do_level1_bounce(self, result):
        if result:
            self._app.set_js_property('collision_0', ('d', 0.1))
        else:
            self._app.set_js_property('collision_0', ('d', 2))

    def do_level2_fric(self, result):
        if result:
            self._app.set_js_property('friction_0', ('i', 5))
        else:
            self._app.set_js_property('friction_0', ('i', 0))

    def do_level2_repulse(self, result):
        if result:
            self._app.set_js_property('socialForce_0_2', ('i', -30))
        else:
            self._app.set_js_property('socialForce_0_2', ('i', 0))

    def do_level3_grav(self, result):
        if result:
            self._app.set_js_property('gravity_0', ('i', 50))
        else:
            self._app.set_js_property('gravity_0', ('i', -50))

    def do_level3_repulse(self, result):
        if result:
            self._app.set_js_property('socialForce_4_3', ('i', -30))
        else:
            self._app.set_js_property('socialForce_4_3', ('i', 0))

    def do_level4_gravgoal(self, result):
        if result:
            self._app.set_js_property('', ('i', -30))
        else:
            self._app.set_js_property('', ('i', 0))

    def do_level4_gravdia(self, result):
        if result:
            self._app.set_js_property('', ('i', -30))
        else:
            self._app.set_js_property('', ('i', 0))

    def do_level4_fricdia(self, result):
        if result:
            self._app.set_js_property('', ('i', -30))
        else:
            self._app.set_js_property('', ('i', 0))

    # # # # # # # # # # # #
    # # # QUEST STEPS # # #
    # # # # # # # # # # # #

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_startgame

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_startgame(self):
        # level 17, 16 internally
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE))
        self.set_tools()
        # this is narrative, don't let the player win early!
        self._app.disable_tool('create')
        self.phys_off()
        return self.step_level1_pre2

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1_pre(self):
        self.wait_confirm('LEVELS1')
        self.wait_confirm('LEVELS1_B')
        self._app.set_js_property('gravity_0', ('i', 50))
        self.phys_on()
        return self.step_level1_pre2

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1_pre2(self):
        self.pause(7)
        self.wait_confirm('LEVELS1_C')
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE))
        self._app.reset()
        self.pause(0.3)
        self.set_tools()
        self.phys_off()
        # ok, now we go to gameplay, give the player a tool
        self._app.disable_tool('create', disabled='False')
        return self.step_level1

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1(self):
        # ensure correct tools are set
        self.set_tools()
        self.show_confirm_message('LEVELS1_READY', confirm_label='Ready!').wait()
        # construct answers and ask parameter question 1
        choiceHigh = ('LEVELS1_Q1_A1', self.do_level1_fric, True)
        choiceLow = ('LEVELS1_Q1_A2', self.do_level1_fric, False)
        self.show_choices_message('LEVELS1_Q1', choiceHigh, choiceLow).wait()
        # construct answers and ask parameter question 2
        choiceHigh = ('LEVELS1_Q2_A1', self.do_level1_bounce, True)
        choiceLow = ('LEVELS1_Q2_A2', self.do_level1_bounce, False)
        self.show_choices_message('LEVELS1_Q2', choiceHigh, choiceLow).wait()
        # give player one last change to add rocks
        self.wait_confirm('LEVELS1_GO')
        # grab current level before we start, for later comparison
        cl = int(self._app.get_current_level())
        logger.debug("current level %i", cl)
        # unfreeze the orange ball
        self.phys_on()
        self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'ballDied'], timeout=15)
        logger.debug("currentLevel changed, ballDied, or time limit occurred")
        # get effective level, if the player won this will be currentLevel+1
        efl = int(self._app.get_effective_level())
        logger.debug("effective level %i", efl)
        if cl == efl:
            # player didn't achieve victory
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.3)
            self.phys_off()
            self.set_tools()
            self.wait_confirm('LEVELS1_FAIL')
            return self.step_level1
        else:
            # player won!
            self.phys_off()
            self.wait_confirm('LEVELS1_FINISH')
            return self.step_level2_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2_pre(self):
        # level 18
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE + 1))
        self.pause(0.3)
        self._app.reset()
        self.pause(0.3)
        self.phys_off()
        self.set_tools()
        self.wait_confirm('LEVELS2')
        return self.step_level2

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2(self):
        self.set_tools()
        self.show_confirm_message('LEVELS2_READY', confirm_label='Ready!').wait()

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
        efl = int(self._app.get_effective_level())

        if cl == efl:
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.3)
            self.phys_off()
            self.set_tools()
            self.wait_confirm('LEVELS2_FAIL')
            return self.step_level2
        else:
            self.phys_off()
            self.wait_confirm('LEVELS2_FINISH')
            if efl > int(self._app.get_current_level()):
                self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            return self.step_level3_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3_pre(self):
        # level 19
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE + 2))
        self.pause(0.3)
        self._app.reset()
        self.pause(0.3)
        self.phys_off()
        self.set_tools()
        self.wait_confirm('LEVELS3')
        return self.step_level3

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3(self):
        self.set_tools()
        self.show_confirm_message('LEVELS3_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS3_Q1_A1', self.do_level3_grav, True)
        choiceLow = ('LEVELS3_Q1_A2', self.do_level3_grav, False)
        self.show_choices_message('LEVELS3_Q1', choiceHigh, choiceLow).wait()

        choiceHigh = ('LEVELS3_Q2_A1', self.do_level3_repulse, True)
        choiceLow = ('LEVELS3_Q2_A2', self.do_level3_repulse, False)
        self.show_choices_message('LEVELS3_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS3_GO')
        cl = int(self._app.get_current_level())
        self.phys_on()
        self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'ballDied'], timeout=15)
        efl = int(self._app.get_effective_level())

        if cl == efl:
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.3)
            self.set_tools()
            self.phys_off()
            self.wait_confirm('LEVELS3_FAIL')
            return self.step_level3
        else:
            self.phys_off()
            self.wait_confirm('LEVELS3_FINISH')
            return self.step_level4_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level4_pre(self):
        # level 20
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE + 3))
        self.pause(0.3)
        self._app.reset()
        self.pause(0.3)
        self.phys_off()
        self.set_tools()
        self.wait_confirm('LEVELS4')
        return self.step_level4

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level4(self):
        self.set_tools()
        self.show_confirm_message('LEVELS4_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS4_Q1_A1', self.do_level4_gravgoal, True)
        choiceLow = ('LEVELS4_Q1_A2', self.do_level4_gravgoal, False)
        self.show_choices_message('LEVELS4_Q1', choiceHigh, choiceLow).wait()

        choiceHigh = ('LEVELS4_Q2_A1', self.do_level4_gravdia, True)
        choiceLow = ('LEVELS4_Q2_A2', self.do_level4_gravdia, False)
        self.show_choices_message('LEVELS4_Q2', choiceHigh, choiceLow).wait()

        choiceHigh = ('LEVELS4_Q3_A1', self.do_level4_fricdia, True)
        choiceLow = ('LEVELS4_Q3_A2', self.do_level4_fricdia, False)
        self.show_choices_message('LEVELS4_Q3', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS4_GO')
        cl = int(self._app.get_current_level())
        self.phys_on()
        self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'ballDied'], timeout=15)
        efl = int(self._app.get_effective_level())

        if cl == efl:
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.3)
            self.set_tools()
            self.phys_off()
            self.wait_confirm('LEVELS4_FAIL')
            return self.step_level4
        else:
            self.phys_off()
            self.wait_confirm('LEVELS4_FINISH')
            return self.step_level5_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level5_pre(self):
        return self.step_level5

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level5(self):
        return self.step_level6_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level6_pre(self):
        return self.step_level6

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level6(self):
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        self.give_item('item.key.sidetrack.2')
        Sound.play('quests/quest-complete')
        self.stop()
