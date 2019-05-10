from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, ToolBoxTopic
from eosclubhouse.apps import Fizzics


class FizzicsKey(Quest):

    __available_after_completing_quests__ = ['MazePt3']
    FIRST_LEVEL = 17

    def __init__(self):
        super().__init__('FizzicsKey', 'saniel')
        self._app = Fizzics()

    # # # # # # # # # # #
    # # UTILITY FXNS  # #
    # # # # # # # # # # #

    def set_tools(self, create_disabled=False):
        self._app.disable_tool('fling')
        self._app.disable_tool('delete')
        self._app.disable_tool('move')
        # make sure we can create, because this is turned off sometimes
        self._app.disable_tool('create', disabled=create_disabled)
        if not create_disabled:
            # disable adding not-rocks
            # can't disable this until AFTER the create tool is set up
            self._app.disable_add_tool_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.GOAL,
                self._app.BallType.ENEMY,
                self._app.BallType.DIAMOND,
            ])

    def setup_level_and_tools(self, level, create_disabled=False):
        self._app.set_current_level(level)
        self._app.reset()
        self.pause(0.2)
        self.set_tools(create_disabled)

    # # # # # # # # # # # # #
    # # QUESTION RESULTS  # #
    # # # # # # # # # # # # #

    def do_level1_friction(self, result):
        friction = 5 if result else 0
        self._app.set_property_for_ball_type('friction', self._app.BallType.PLAYER, ('i', friction))

    def do_level1_bounce(self, result):
        bounce = 0.1 if result else 2
        self._app.set_property_for_ball_type('collision', self._app.BallType.PLAYER, ('d', bounce))

    def do_level2_friction(self, result):
        friction = 5 if result else 0
        self._app.set_property_for_ball_type('friction', self._app.BallType.PLAYER, ('i', friction))

    def do_level2_repel(self, result):
        repel = -30 if result else 0
        self._app.set_socialforce_for_ball_to_ball(self._app.BallType.PLAYER,
                                                   self._app.BallType.ENEMY, ('i', repel))

    def do_level3_gravity(self, result):
        gravity = 50 if result else -50
        self._app.set_property_for_ball_type('gravity', self._app.BallType.PLAYER, ('i', gravity))

    def do_level3_repel(self, result):
        repel = -30 if result else 0
        self._app.set_socialforce_for_ball_to_ball(self._app.BallType.DIAMOND,
                                                   self._app.BallType.ROCK, ('i', repel))

    def do_level4_gravity_goal(self, result):
        gravity = 50 if result else 0
        self._app.set_property_for_ball_type('gravity', self._app.BallType.GOAL, ('i', gravity))

    def do_level4_gravity_diamond(self, result):
        gravity = 50 if result else 0
        self._app.set_property_for_ball_type('gravity', self._app.BallType.DIAMOND, ('i', gravity))

    def do_level4_friction_diamond(self, result):
        friction = 2.5 if result else 0
        self._app.set_property_for_ball_type('friction', self._app.BallType.DIAMOND,
                                             ('d', friction))

    def do_level5_gravity_goal(self, result):
        gravity = 50 if result else 0
        self._app.set_property_for_ball_type('gravity', self._app.BallType.GOAL, ('i', gravity))

    def do_level5_size_diamond(self, result):
        size = 100 if result else 35
        self._app.set_property_for_ball_type('radius', self._app.BallType.DIAMOND, ('d', size))

    def do_level6_gravity_negative(self, result):
        gravity = -25 if result else -200
        self._app.set_property_for_ball_type('gravity', self._app.BallType.PLAYER, ('i', gravity))

    def do_level6_repel(self, result):
        repel = -30 if result else 0
        self._app.set_socialforce_for_ball_to_ball(self._app.BallType.ROCK,
                                                   self._app.BallType.PLAYER, ('i', repel))

    # # # # # # # # # # # #
    # # # QUEST STEPS # # #
    # # # # # # # # # # # #

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        toolbox_topic = ToolBoxTopic(self._app.APP_NAME, 'main')
        toolbox_topic.set_sensitive(False)
        return self.step_ingame

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_ingame(self):
        # level 17, 16 internally
        # this is narrative, don't let the player win early!
        self.setup_level_and_tools(self.FIRST_LEVEL, create_disabled=True)
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
        ], enable=False)
        return self.step_level1_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1_pre(self):
        self.wait_confirm('LEVELS1')
        self.wait_confirm('LEVELS1_B')
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
        ], enable=True)
        return self.step_level1_pre2

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1_pre2(self):
        self.pause(7)
        self.wait_confirm('LEVELS1_C')
        self.setup_level_and_tools(self.FIRST_LEVEL)
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
        ], enable=False)
        return self.step_level1

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1(self):
        current_level = self._app.get_current_level()
        self.show_confirm_message('LEVELS1_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS1_Q1_A1', self.do_level1_friction, True)
        choiceLow = ('LEVELS1_Q1_A2', self.do_level1_friction, False)
        self.show_choices_message('LEVELS1_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS1_Q2_A1', self.do_level1_bounce, True)
        choiceLow = ('LEVELS1_Q2_A2', self.do_level1_bounce, False)
        self.show_choices_message('LEVELS1_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS1_GO')
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
        ], enable=True)
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self.setup_level_and_tools(current_level)
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.DIAMOND,
            ], enable=False)
            self.wait_confirm('LEVELS1_FAIL')
            return self.step_level1
        else:
            self._app.enable_physics_for_ball_type(self._app.BallType.PLAYER, enable=False)
            self.pause(0.2)
            self.wait_confirm('LEVELS1_FINISH')
            return self.step_level2_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2_pre(self):
        # level 18
        self.setup_level_and_tools(self.FIRST_LEVEL + 1)
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
        ], enable=False)
        self.wait_confirm('LEVELS2')
        return self.step_level2

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2(self):
        current_level = self._app.get_current_level()
        self.show_confirm_message('LEVELS2_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS2_Q1_A1', self.do_level2_repel, True)
        choiceLow = ('LEVELS2_Q1_A2', self.do_level2_repel, False)
        self.show_choices_message('LEVELS2_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS2_Q2_A1', self.do_level2_friction, True)
        choiceLow = ('LEVELS2_Q2_A2', self.do_level2_friction, False)
        self.show_choices_message('LEVELS2_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS2_GO')
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
        ], enable=True)
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self.setup_level_and_tools(current_level)
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.DIAMOND,
            ], enable=False)
            self.wait_confirm('LEVELS2_FAIL')
            return self.step_level2
        else:
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.DIAMOND,
            ], enable=False)
            self.pause(0.2)
            self.wait_confirm('LEVELS2_FINISH')
            return self.step_level3_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3_pre(self):
        # level 19
        self.setup_level_and_tools(self.FIRST_LEVEL + 2)
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
            self._app.BallType.GOAL,
        ], enable=False)
        self.wait_confirm('LEVELS3')
        return self.step_level3

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3(self):
        current_level = self._app.get_current_level()
        self.show_confirm_message('LEVELS3_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS3_Q1_A1', self.do_level3_gravity, True)
        choiceLow = ('LEVELS3_Q1_A2', self.do_level3_gravity, False)
        self.show_choices_message('LEVELS3_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS3_Q2_A1', self.do_level3_repel, True)
        choiceLow = ('LEVELS3_Q2_A2', self.do_level3_repel, False)
        self.show_choices_message('LEVELS3_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS3_GO')
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
            self._app.BallType.GOAL,
        ], enable=True)
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self.setup_level_and_tools(current_level)
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.DIAMOND,
                self._app.BallType.GOAL,
            ], enable=False)
            self.wait_confirm('LEVELS3_FAIL')
            return self.step_level3
        else:
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.DIAMOND,
                self._app.BallType.GOAL,
            ], enable=False)
            self.pause(0.2)
            self.wait_confirm('LEVELS3_FINISH')
            return self.step_level4_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level4_pre(self):
        # level 20
        self.setup_level_and_tools(self.FIRST_LEVEL + 3)
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
            self._app.BallType.GOAL,
        ], enable=False)
        self.wait_confirm('LEVELS4')
        return self.step_level4

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level4(self):
        current_level = self._app.get_current_level()
        self.show_confirm_message('LEVELS4_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS4_Q1_A1', self.do_level4_gravity_goal, True)
        choiceLow = ('LEVELS4_Q1_A2', self.do_level4_gravity_goal, False)
        self.show_choices_message('LEVELS4_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS4_Q2_A1', self.do_level4_gravity_diamond, True)
        choiceLow = ('LEVELS4_Q2_A2', self.do_level4_gravity_diamond, False)
        self.show_choices_message('LEVELS4_Q2', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS4_Q3_A1', self.do_level4_friction_diamond, True)
        choiceLow = ('LEVELS4_Q3_A2', self.do_level4_friction_diamond, False)
        self.show_choices_message('LEVELS4_Q3', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS4_GO')
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
            self._app.BallType.GOAL,
        ], enable=True)
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self.setup_level_and_tools(current_level)
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.DIAMOND,
                self._app.BallType.GOAL,
            ], enable=False)
            self.wait_confirm('LEVELS4_FAIL')
            return self.step_level4
        else:
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.DIAMOND,
                self._app.BallType.GOAL,
            ], enable=False)
            self.pause(0.2)
            self.wait_confirm('LEVELS4_FINISH')
            return self.step_level5_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level5_pre(self):
        # level 21
        self.setup_level_and_tools(self.FIRST_LEVEL + 4)
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
            self._app.BallType.GOAL,
        ], enable=False)
        self.wait_confirm('LEVELS5')
        return self.step_level5

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level5(self):
        current_level = self._app.get_current_level()
        self.show_confirm_message('LEVELS5_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS5_Q1_A1', self.do_level5_gravity_goal, True)
        choiceLow = ('LEVELS5_Q1_A2', self.do_level5_gravity_goal, False)
        self.show_choices_message('LEVELS5_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS5_Q2_A1', self.do_level5_size_diamond, True)
        choiceLow = ('LEVELS5_Q2_A2', self.do_level5_size_diamond, False)
        self.show_choices_message('LEVELS5_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS5_GO')
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.DIAMOND,
            self._app.BallType.GOAL,
        ], enable=True)
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self.setup_level_and_tools(current_level)
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.DIAMOND,
                self._app.BallType.GOAL,
            ], enable=False)
            self.wait_confirm('LEVELS5_FAIL')
            return self.step_level5
        else:
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.DIAMOND,
                self._app.BallType.GOAL,
            ], enable=False)
            self.pause(0.2)
            self.wait_confirm('LEVELS5_FINISH')
            return self.step_level6_pre

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level6_pre(self):
        # level 22
        self.setup_level_and_tools(self.FIRST_LEVEL + 5)
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.GOAL,
        ], enable=False)
        self.wait_confirm('LEVELS6')
        return self.step_level6

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level6(self):
        current_level = self._app.get_current_level()
        self.show_confirm_message('LEVELS6_READY', confirm_label='Ready!').wait()

        choiceHigh = ('LEVELS6_Q1_A1', self.do_level6_gravity_negative, True)
        choiceLow = ('LEVELS6_Q1_A2', self.do_level6_gravity_negative, False)
        self.show_choices_message('LEVELS6_Q1', choiceHigh, choiceLow).wait()
        choiceHigh = ('LEVELS6_Q2_A1', self.do_level6_repel, True)
        choiceLow = ('LEVELS6_Q2_A2', self.do_level6_repel, False)
        self.show_choices_message('LEVELS6_Q2', choiceHigh, choiceLow).wait()

        self.wait_confirm('LEVELS6_GO')
        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
            self._app.BallType.GOAL,
        ], enable=True)
        self.wait_for_app_js_props_changed(self._app, ['levelSuccess', 'ballDied'], timeout=15)
        if not self._app.get_js_property('levelSuccess'):
            self.setup_level_and_tools(current_level)
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.GOAL,
            ], enable=False)
            self.wait_confirm('LEVELS6_FAIL')
            return self.step_level6
        else:
            self._app.enable_physics_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.GOAL,
            ], enable=False)
            self.pause(0.2)
            return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        self.give_item('item.key.sidetrack.2')
        Sound.play('quests/quest-complete')
        self.stop()
