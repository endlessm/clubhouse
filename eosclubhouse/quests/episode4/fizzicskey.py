from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Fizzics
from eosclubhouse import logger
from gi.repository import GLib, Gio


class FizzicsKey(Quest):

    __available_after_completing_quests__ = ['MazePt3']
    PRESET_NUM = 16

    def __init__(self):
        super().__init__('FizzicsKey', 'saniel')
        self._app = Fizzics()

    def reset_params(self):
        # found the defaults
        self.phys_off()
        self._app.set_js_property('gravity_0', ('u', 0))
        self._app.set_js_property('friction_0', ('u', 10))
        self._app.set_js_property('collision_0', ('d', 0.2))
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

    def do_result_grav(self, result):
        if result:
            self._app.set_js_property('gravity_0', ('u', 200))
        else:
            self._app.set_js_property('gravity_0', ('u', 20))

    def do_result_fric(self, result):
        if result:
            self._app.set_js_property('friction_0', ('u', 50))
        else:
            self._app.set_js_property('friction_0', ('u', 1))

    def do_result_bounce(self, result):
        if result:
            self._app.set_js_property('collision_0', ('d', 0.4))
        else:
            self._app.set_js_property('collision_0', ('d', 0.05))

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_ingame

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_ingame(self):
        # get to level
        self._app.set_js_property('preset', ('i', self.PRESET_NUM))
        # freeze physics and set values to normal
        self.reset_params()
        cl = int(self._app.get_current_level())
        if cl != 17:
            logger.debug("PROBLEM - Not at 17 (16 internal), at level %i", cl)
        return self.step_level1

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1(self):
        while self._app.get_js_property('usePhysics_0') is not True:
            self.phys_off()
        self.reset_params()
        cl = int(self._app.get_current_level())
        logger.debug("level is %i", cl)
        # present the choice of value
        choiceHigh = ('CHOICEHIGH', self.do_result_grav, True)
        choiceLow = ('CHOICELOW', self.do_result_grav, False)
        self.show_choices_message('SETGRAV', choiceHigh, choiceLow).wait()
        # after choice chosen, activate physics
        logger.debug("choice chosen")
        self.wait_confirm('DUMMY1')
        self.phys_on()
        # test here if the player won, otherwise restart
        self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'ballDied'], timeout=30)
        logger.debug("currentLevel changed, ballDied, or time limit occurred")
        self.phys_off()
        self.reset_params()
        if self._app.get_current_level() > cl:
            logger.debug("current level > cl, means you won")
            return self.step_level2
        else:
            logger.debug("currentLevel not greater than cl, you didn't win")
            logger.debug("change level to current level and restart")
            self._app.set_js_property('preset', ('i', cl - 1))
            return self.step_level1

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2(self):
        self.reset_params()
        choiceHigh = ('CHOICEHIGH', self.do_result_fric, True)
        choiceLow = ('CHOICELOW', self.do_result_fric, False)
        self.show_choices_message('SETFRIC', choiceHigh, choiceLow).wait()
        self._app.set_js_property('usePhysics_0', ('b', True))
        self.wait_confirm('DUMMY3')
        self.reset_params()
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
        self.wait_confirm('DUMMY3')
        self.complete = True
        self.available = False
        self.give_item('item.key.sidetrack.2')
        Sound.play('quests/quest-complete')
        self.stop()
