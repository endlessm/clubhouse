from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, ToolBoxTopic
from eosclubhouse.apps import Fizzics


class FizzicsKey(Quest):

    __available_after_completing_quests__ = ['MazePt3']
    FIRST_LEVEL = 17
    LAST_LEVEL = FIRST_LEVEL + 5

    QUESTIONS = {
        FIRST_LEVEL: [
            ('LEVELS1_Q1', 'LEVELS1_Q1_A1', 'LEVELS1_Q1_A2', 'do_level1_friction'),
            ('LEVELS1_Q2', 'LEVELS1_Q2_A1', 'LEVELS1_Q2_A2', 'do_level1_bounce'),
        ],
        FIRST_LEVEL + 1: [
            ('LEVELS2_Q1', 'LEVELS2_Q1_A1', 'LEVELS2_Q1_A2', 'do_level2_repel'),
            ('LEVELS2_Q2', 'LEVELS2_Q2_A1', 'LEVELS2_Q2_A2', 'do_level2_friction'),
        ],
        FIRST_LEVEL + 2: [
            ('LEVELS3_Q1', 'LEVELS3_Q1_A1', 'LEVELS3_Q1_A2', 'do_level3_gravity'),
            ('LEVELS3_Q2', 'LEVELS3_Q2_A1', 'LEVELS3_Q2_A2', 'do_level3_repel'),
        ],
        FIRST_LEVEL + 3: [
            ('LEVELS4_Q1', 'LEVELS4_Q1_A1', 'LEVELS4_Q1_A2', 'do_level4_gravity_goal'),
            ('LEVELS4_Q2', 'LEVELS4_Q2_A1', 'LEVELS4_Q2_A2', 'do_level4_gravity_diamond'),
            ('LEVELS4_Q3', 'LEVELS4_Q3_A1', 'LEVELS4_Q3_A2', 'do_level4_friction_diamond'),
        ],
        FIRST_LEVEL + 4: [
            ('LEVELS5_Q1', 'LEVELS5_Q1_A1', 'LEVELS5_Q1_A2', 'do_level5_gravity_goal'),
            ('LEVELS5_Q2', 'LEVELS5_Q2_A1', 'LEVELS5_Q2_A2', 'do_level5_size_diamond'),
        ],
        FIRST_LEVEL + 5: [
            ('LEVELS6_Q1', 'LEVELS6_Q1_A1', 'LEVELS6_Q1_A2', 'do_level6_gravity_negative'),
            ('LEVELS6_Q2', 'LEVELS6_Q2_A1', 'LEVELS6_Q2_A2', 'do_level6_repel'),
        ],
    }

    BALLS_TO_UNFREEZE = {
        FIRST_LEVEL: [
            Fizzics.BallType.PLAYER,
        ],
        FIRST_LEVEL + 1: [
            Fizzics.BallType.PLAYER,
            Fizzics.BallType.DIAMOND,
        ],
        FIRST_LEVEL + 2: [
            Fizzics.BallType.PLAYER,
            Fizzics.BallType.DIAMOND,
            Fizzics.BallType.GOAL,
        ],
        FIRST_LEVEL + 3: [
            Fizzics.BallType.PLAYER,
            Fizzics.BallType.DIAMOND,
            Fizzics.BallType.GOAL,
        ],
        FIRST_LEVEL + 4: [
            Fizzics.BallType.PLAYER,
            Fizzics.BallType.DIAMOND,
            Fizzics.BallType.GOAL,
        ],
        FIRST_LEVEL + 5: [
            Fizzics.BallType.PLAYER,
            Fizzics.BallType.GOAL,
        ],
    }

    def __init__(self):
        super().__init__('FizzicsKey', 'saniel')
        self._app = Fizzics()
        self._intro_cutscene_played = False
        self._toolbox_topic = None

    # # # # # # # # # # #
    # # UTILITY FXNS  # #
    # # # # # # # # # # #

    def setup_level_and_tools(self, level, create_disabled=False):
        self._app.set_current_level(level)
        self.pause(0.2)
        if self._app.get_js_property('levelLoading', True):
            self.wait_for_app_js_props_changed(self._app, ['levelLoading'])

        self._app.disable_tool('fling')
        self._app.disable_tool('delete')
        self._app.disable_tool('move')
        self._app.disable_tool('create', disabled=create_disabled)

        if not create_disabled:
            # disable adding not-rocks
            # can't disable this until AFTER the create tool is set up
            self.pause(0.2)
            self._app.disable_add_tool_for_ball_type([
                self._app.BallType.PLAYER,
                self._app.BallType.GOAL,
                self._app.BallType.ENEMY,
                self._app.BallType.DIAMOND,
            ])

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
        self._toolbox_topic = ToolBoxTopic(self._app.APP_NAME, 'main')
        self._intro_cutscene_played = False
        return self.step_level1_pre

    def _get_strings_level(self, level_number):
        # This is the string corresponding to the level as used by
        # messages.
        return int(level_number) - 16

    def _wait_for_action_or_level_change(self, action, timeout=None):
        current_level = self._app.get_current_level()

        actions = [
            action,
            self.connect_app_js_props_changes(self._app, ['currentLevel', 'flipped']),
        ]

        self.wait_for_one(actions, timeout)

        flipped = self._app.get_js_property('flipped', False)
        if flipped:
            return self.step_flipped, None

        level = self._app.get_current_level()
        if level != current_level:
            return self.step_decide_level, {'level_number': level}

        return None, None

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_flipped(self, options=None):
        self._toolbox_topic.set_sensitive(False)
        self.connect_app_js_props_changes(self._app, ['flipped']).wait()
        level = self._app.get_current_level()
        return self.step_decide_level, {'level_number': level}

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_decide_level(self, options):
        level_number = options['level_number']
        if self.FIRST_LEVEL == level_number and not self._intro_cutscene_played:
            return self.step_level1_pre

        if self.FIRST_LEVEL <= level_number <= self.LAST_LEVEL:
            message_id = 'LEVELS1_C' if level_number == self.FIRST_LEVEL else None
            return self.step_level_pre, level_number, message_id

        # The player went to a level outside of the range this quest
        # handles, so begin again:
        if self._intro_cutscene_played:
            return self.step_level_pre, self.FIRST_LEVEL, 'LEVELS1_C'
        return self.step_begin

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1_pre(self):
        # this is narrative, don't let the player win early!
        self.setup_level_and_tools(self.FIRST_LEVEL, create_disabled=True)

        for message_id in ['LEVELS1', 'LEVELS1_B']:
            action = self.show_confirm_message(message_id)
            next_step, options = self._wait_for_action_or_level_change(action)
            if next_step is not None:
                return next_step, options

        self._app.enable_physics_for_ball_type([
            self._app.BallType.PLAYER,
        ])
        self.pause(7)
        self._intro_cutscene_played = True
        return self.step_level_pre, self.FIRST_LEVEL, 'LEVELS1_C'

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level_pre(self, level_number, message_id=None):
        if message_id is None:
            strings_level = self._get_strings_level(level_number)
            message_id = 'LEVELS{}'.format(strings_level)

        self.setup_level_and_tools(level_number)

        action = self.show_confirm_message(message_id)
        next_step, options = self._wait_for_action_or_level_change(action)
        if next_step is not None:
            return next_step, options

        return self.step_level, level_number

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level(self, level_number):
        strings_level = self._get_strings_level(level_number)
        action_ready = self.show_confirm_message('LEVELS{}_READY'.format(strings_level),
                                                 confirm_label='Ready!')
        next_step, options = self._wait_for_action_or_level_change(action_ready)
        if next_step is not None:
            return next_step, options

        for description, option_true, option_false, callback_name in self.QUESTIONS[level_number]:
            callback = getattr(self, callback_name)
            choice_true = (option_true, callback, True)
            choice_false = (option_false, callback, False)
            action_choice = self.show_choices_message(description, choice_true, choice_false)
            next_step, options = self._wait_for_action_or_level_change(action_choice)
            if next_step is not None:
                return next_step, options

        action_go = self.show_confirm_message('LEVELS{}_GO'.format(strings_level))
        next_step, options = self._wait_for_action_or_level_change(action_go)
        if next_step is not None:
            return next_step, options

        self._app.enable_physics_for_ball_type(self.BALLS_TO_UNFREEZE[level_number])

        action_play = self.connect_app_js_props_changes(self._app, ['levelSuccess', 'ballDied'])
        next_step, options = self._wait_for_action_or_level_change(action_play, timeout=15)
        if next_step is not None:
            return next_step, options

        # Has failed?
        if not self._app.get_js_property('levelSuccess'):
            message_id = 'LEVELS{}_FAIL'.format(strings_level)
            return self.step_level_pre, level_number, message_id

        # Has beated the final level?
        if level_number == self.LAST_LEVEL:
            return self.step_success

        # Must have beated a previous level then:
        self.pause(0.2)
        action_finish = self.show_confirm_message('LEVELS{}_FINISH'.format(strings_level))
        next_step, options = self._wait_for_action_or_level_change(action_finish)
        if next_step is not None:
            return next_step, options

        return self.step_level_pre, level_number + 1

    def step_success(self):
        self.pause(0.2)
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        self.give_item('item.key.sidetrack.2')
        Sound.play('quests/quest-complete')
        self.stop()
