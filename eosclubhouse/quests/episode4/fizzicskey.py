from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Fizzics


class FizzicsKey(Quest):

    __available_after_completing_quests__ = ['MazePt3']

    def __init__(self):
        super().__init__('FizzicsKey', 'Saniel')
        self._app = Fizzics()
        self._gParams = 'view.JSContext.globalParameters'

    def reset_params(self):
        # TODO: What are the default values for these?
        self._app.set_object_property(self._gParams, 'usePhysics_0', ('b', False))
        self._app.set_object_property(self._gParams, 'gravity_0', ('u', 100))
        self._app.set_object_property(self._gParams, 'friction_0', ('u', 100))
        self._app.set_object_property(self._gParams, 'collision_0', ('d', 0.1))

    def do_result_grav(self, result):
        if result:
            self._app.set_object_property(self._gParams, 'gravity_0', ('u', 999))
        else:
            self._app.set_object_property(self._gParams, 'gravity_0', ('u', 20))

    def do_result_fric(self, result):
        if result:
            self._app.set_object_property(self._gParams, 'friction_0', ('u', 999))
        else:
            self._app.set_object_property(self._gParams, 'friction_0', ('u', 0))

    def do_result_bounce(self, result):
        if result:
            self._app.set_object_property(self._gParams, 'collision_0', ('d', 10))
        else:
            self._app.set_object_property(self._gParams, 'collision_0', ('d', 0.01))

    def step_begin(self):
        self.ask_for_app_launch(self._app)
        # get the player to the 'old' levels
        # disable tools
        # self._app.disable_tool('fling')
        # self._app.disable_tool('move')
        # self._app.disable_tool('delete')
        # found a better way to do it? This way prevents the visual desync
        self._app.set_object_property(self._gParams, 'flingToolDisabled', ('b', True))
        self._app.set_object_property(self._gParams, 'moveToolDisabled', ('b', True))
        # self._app.set_object_property(self._gParams, 'deleteToolDisabled', ('b', True))
        # re-enable the delete tool for testing
        self._app.set_object_property(self._gParams, 'deleteToolDisabled', ('b', False))
        self._app.set_object_property(self._gParams, 'createToolDisabled', ('b', False))
        # Make tools visible
        self._app.set_object_property(self._gParams, 'flingToolActive', ('b', True))
        self._app.set_object_property(self._gParams, 'moveToolActive', ('b', True))
        self._app.set_object_property(self._gParams, 'deleteToolActive', ('b', True))
        self._app.set_object_property(self._gParams, 'createToolActive', ('b', True))
        # self._app.disable_tool('add', False)
        self.reset_params()
        return self.step_ingame

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_ingame(self):
        self.wait_confirm('DUMMY1')
        self.wait_confirm('DUMMY2')
        # return self.step_success
        return self.step_level1

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1(self):
        # present the choice of value
        choiceHigh = ('CHOICEHIGH', self.do_result_grav, True)
        choiceLow = ('CHOICELOW', self.do_result_grav, False)
        self.show_choices_message('SETGRAV', choiceHigh, choiceLow).wait()
        # after choice chosen, activate physics
        self._app.set_object_property(self._gParams, 'usePhysics_0', ('b', True))
        # test here if the player won, otherwise restart
        # yay you did it
        self.wait_confirm('DUMMY3')
        # next level
        self.reset_params()
        return self.step_level2

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2(self):
        choiceHigh = ('CHOICEHIGH', self.do_result_fric, True)
        choiceLow = ('CHOICELOW', self.do_result_fric, False)
        self.show_choices_message('SETFRIC', choiceHigh, choiceLow).wait()
        self._app.set_object_property(self._gParams, 'usePhysics_0', ('b', True))
        self.wait_confirm('DUMMY3')
        self.reset_params()
        return self.step_level3

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3(self):
        choiceHigh = ('CHOICEHIGH', self.do_result_bounce, True)
        choiceLow = ('CHOICELOW', self.do_result_bounce, False)
        self.show_choices_message('SETBOUNCE', choiceHigh, choiceLow).wait()
        self._app.set_object_property(self._gParams, 'usePhysics_0', ('b', True))
        self.wait_confirm('DUMMY3')
        self.reset_params()
        return self.step_success

    def step_success(self):
        self.wait_confirm('DUMMY3')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
