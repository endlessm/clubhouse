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

    # def reset_params(self):
    #     # found the defaults
    #     self._app.set_js_property('gravity_0', ('i', 0))
    #     self._app.set_js_property('friction_0', ('i', 10))
    #     self._app.set_js_property('collision_0', ('d', 0.2))

    def set_tools(self):
        self._app.disable_tool('fling')
        self._app.disable_tool('delete')
        self._app.disable_tool('move')
        # make sure we can create, because this is turned off sometimes
        self._app.disable_tool('create', disabled=False)
        # Make tools visible (must do this to prevent desync)
        self._app.set_js_property('flingToolActive', ('b', False))
        self._app.set_js_property('moveToolActive', ('b', False))
        self._app.set_js_property('deleteToolActive', ('b', False))
        self._app.set_js_property('createToolActive', ('b', True))
        # disable adding not-rocks
        # can't disable this until AFTER the create tool is set up
        self._app.disable_add_tool_for_ball_type(0)
        self._app.disable_add_tool_for_ball_type(1)
        self._app.disable_add_tool_for_ball_type(2)
        self._app.disable_add_tool_for_ball_type(4)

    def phys_off(self):
        self._app.set_js_property('usePhysics_0', ('b', False))
        # logger.debug("set physics0 OFF-DISABLED (%s)", self._app.get_js_property('usePhysics_0'))

    def phys_on(self):
        self._app.set_js_property('usePhysics_0', ('b', True))
        # logger.debug("set physics0 ON-ENABLED (%s)", self._app.get_js_property('usePhysics_0'))

    def phys_off_goal(self):
        self._app.set_js_property('usePhysics_1', ('b', False))

    def phys_on_goal(self):
        self._app.set_js_property('usePhysics_1', ('b', True))

    def phys_off_dia(self):
        self._app.set_js_property('usePhysics_4', ('b', False))

    def phys_on_dia(self):
        self._app.set_js_property('usePhysics_4', ('b', True))

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
            self._app.set_js_property('gravity_1', ('i', 50))
        else:
            self._app.set_js_property('gravity_1', ('i', 0))

    def do_level4_gravdia(self, result):
        if result:
            self._app.set_js_property('gravity_4', ('i', 50))
        else:
            self._app.set_js_property('gravity_4', ('i', 0))

    def do_level4_fricdia(self, result):
        if result:
            self._app.set_js_property('friction_4', ('d', 2.5))
        else:
            self._app.set_js_property('friction_4', ('d', 0))

    def do_level5_gravgoal(self, result):
        if result:
            self._app.set_js_property('gravity_1', ('i', 50))
        else:
            self._app.set_js_property('gravity_1', ('i', 0))

    def do_level5_sizedia(self, result):
        if result:
            self._app.set_js_property('radius_4', ('d', 100))
        else:
            self._app.set_js_property('radius_4', ('d', 35))

    def do_level6_gravneg(self, result):
        if result:
            self._app.set_js_property('gravity_0', ('i', -25))
        else:
            self._app.set_js_property('gravity_0', ('i', -200))

    def do_level6_repel(self, result):
        if result:
            self._app.set_js_property('socialForce_3_0', ('i', -30))
        else:
            self._app.set_js_property('socialForce_3_0', ('i', 0))

    # # # # # # # # # # # #
    # # # QUEST STEPS # # #
    # # # # # # # # # # # #

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_ingame

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_ingame(self):
        # level 17, 16 internally
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE))
        self.set_tools()
        # this is narrative, don't let the player win early!
        self._app.disable_tool('create')
        self.phys_off()
        self.phys_off_dia()
        return self.step_level1_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1_pre(self):
        self.wait_confirm('LEVELS1')
        self.wait_confirm('LEVELS1_B')
        self._app.set_js_property('gravity_0', ('i', 50))
        self.phys_on()
        self.phys_on_dia()
        return self.step_level1_pre2

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1_pre2(self):
        self.pause(7)
        self.wait_confirm('LEVELS1_C')
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE))
        self._app.reset()
        self.pause(0.2)
        self.set_tools()
        self.phys_off()
        self.phys_off_dia()
        # ok, now we go to gameplay, give the player a tool
        self._app.disable_tool('create', disabled='False')
        return self.step_level1

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1(self):
        cl = int(self._app.get_current_level())
        logger.debug("current level %i", cl)
        # ensure correct tools are set
        self.set_tools()
        cl = int(self._app.get_current_level())
        self.show_confirm_message('LEVELS1_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS1_Q1_A1', self.do_level1_fric, True)
        choiceLow = ('LEVELS1_Q1_A2', self.do_level1_fric, False)
        self.show_choices_message('LEVELS1_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS1_Q2_A1', self.do_level1_bounce, True)
        choiceLow = ('LEVELS1_Q2_A2', self.do_level1_bounce, False)
        self.show_choices_message('LEVELS1_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS1_GO')
        # unfreeze the orange ball
        self.phys_on()
        self.phys_on_dia()
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.2)
            self.phys_off()
            self.phys_off_dia()
            self.set_tools()
            self.wait_confirm('LEVELS1_FAIL')
            return self.step_level1
        else:
            self.phys_off()
            self.pause(0.2)
            self.wait_confirm('LEVELS1_FINISH')
            return self.step_level2_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2_pre(self):
        # level 18
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE + 1))
        self.phys_off()
        self.pause(0.1)
        self._app.reset()
        self.pause(0.1)
        self.phys_off()
        self.phys_off_dia()
        self.set_tools()
        self.wait_confirm('LEVELS2')
        return self.step_level2

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2(self):
        cl = int(self._app.get_current_level())
        self.set_tools()
        self.show_confirm_message('LEVELS2_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS2_Q1_A1', self.do_level2_repulse, True)
        choiceLow = ('LEVELS2_Q1_A2', self.do_level2_repulse, False)
        self.show_choices_message('LEVELS2_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS2_Q2_A1', self.do_level2_fric, True)
        choiceLow = ('LEVELS2_Q2_A2', self.do_level2_fric, False)
        self.show_choices_message('LEVELS2_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS2_GO')
        self.phys_on()
        self.phys_on_dia()
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.2)
            self.phys_off()
            self.phys_off_dia()
            self.set_tools()
            self.wait_confirm('LEVELS2_FAIL')
            return self.step_level2
        else:
            self.phys_off()
            self.phys_off_dia()
            self.pause(0.2)
            self.wait_confirm('LEVELS2_FINISH')
            return self.step_level3_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3_pre(self):
        # level 19
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE + 2))
        self.pause(0.2)
        self._app.reset()
        self.pause(0.2)
        self._app.reset()
        self.pause(0.2)
        self.phys_off()
        self.phys_off_dia()
        self.phys_off_goal()
        self.set_tools()
        self.wait_confirm('LEVELS3')
        return self.step_level3

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3(self):
        cl = int(self._app.get_current_level())
        self.set_tools()
        self.show_confirm_message('LEVELS3_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS3_Q1_A1', self.do_level3_grav, True)
        choiceLow = ('LEVELS3_Q1_A2', self.do_level3_grav, False)
        self.show_choices_message('LEVELS3_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS3_Q2_A1', self.do_level3_repulse, True)
        choiceLow = ('LEVELS3_Q2_A2', self.do_level3_repulse, False)
        self.show_choices_message('LEVELS3_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS3_GO')
        self.phys_on()
        self.phys_on_dia()
        self.phys_on_goal()
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.2)
            self.set_tools()
            self.phys_off()
            self.phys_off_dia()
            self.phys_off_goal()
            self.wait_confirm('LEVELS3_FAIL')
            return self.step_level3
        else:
            self.phys_off()
            self.phys_off_dia()
            self.phys_off_goal()
            self.pause(0.2)
            self.wait_confirm('LEVELS3_FINISH')
            return self.step_level4_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level4_pre(self):
        # level 20
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE + 3))
        self.pause(0.2)
        self._app.reset()
        self.pause(0.2)
        self.phys_off()
        self.phys_off_dia()
        self.phys_off_goal()
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
        self.phys_on_dia()
        self.phys_on_goal()
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.2)
            self.set_tools()
            self.phys_off()
            self.phys_off_dia()
            self.phys_off_goal()
            self.wait_confirm('LEVELS4_FAIL')
            return self.step_level4
        else:
            self.phys_off()
            self.phys_off_dia()
            self.phys_off_goal()
            self.pause(0.2)
            self.wait_confirm('LEVELS4_FINISH')
            return self.step_level5_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level5_pre(self):
        # level 21
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE + 4))
        self.pause(0.2)
        self._app.reset()
        self.pause(0.1)
        self.phys_off()
        self.phys_off_dia()
        self.phys_off_goal()
        self.set_tools()
        self.wait_confirm('LEVELS5')
        return self.step_level5

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level5(self):
        self.set_tools()
        self.show_confirm_message('LEVELS5_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS5_Q1_A1', self.do_level5_gravgoal, True)
        choiceLow = ('LEVELS5_Q1_A2', self.do_level5_gravgoal, False)
        self.show_choices_message('LEVELS5_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS5_Q2_A1', self.do_level5_sizedia, True)
        choiceLow = ('LEVELS5_Q2_A2', self.do_level5_sizedia, False)
        self.show_choices_message('LEVELS5_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS5_GO')
        cl = int(self._app.get_current_level())
        self.phys_on()
        self.phys_on_dia()
        self.phys_on_goal()
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.1)
            self.set_tools()
            self.phys_off()
            self.phys_off_dia()
            self.phys_off_goal()
            self.wait_confirm('LEVELS5_FAIL')
            return self.step_level5
        else:
            self.phys_off()
            self.phys_off_dia()
            self.phys_off_goal()
            self.pause(0.1)
            self.wait_confirm('LEVELS5_FINISH')
            return self.step_level6_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level6_pre(self):
        # level 22
        self._app.set_js_property('preset', ('i', self.PRESET_NUM_BASE + 5))
        self.pause(0.1)
        self._app.reset()
        self.pause(0.1)
        self.phys_off()
        self.phys_off_goal()
        self.set_tools()
        self.wait_confirm('LEVELS6')
        return self.step_level6

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level6(self):
        self.set_tools()
        self.show_confirm_message('LEVELS6_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS6_Q1_A1', self.do_level6_gravneg, True)
        choiceLow = ('LEVELS6_Q1_A2', self.do_level6_gravneg, False)
        self.show_choices_message('LEVELS6_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS6_Q2_A1', self.do_level6_repel, True)
        choiceLow = ('LEVELS6_Q2_A2', self.do_level6_repel, False)
        self.show_choices_message('LEVELS6_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS6_GO')
        cl = int(self._app.get_current_level())
        self.phys_on()
        self.phys_on_goal()
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self._app.set_js_property('preset', ('i', cl - 1))
            self._app.reset()
            self.pause(0.1)
            self.set_tools()
            self.phys_off()
            self.phys_off_goal()
            self.wait_confirm('LEVELS6_FAIL')
            return self.step_level6
        else:
            self.phys_off()
            self.phys_off_goal()
            self.pause(0.1)
            return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        self.give_item('item.key.sidetrack.2')
        Sound.play('quests/quest-complete')
        self.stop()
