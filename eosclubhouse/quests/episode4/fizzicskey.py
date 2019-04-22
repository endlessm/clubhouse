from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Fizzics

class FizzicsKey(Quest):

    __available_after_completing_quests__ = ['MazePt3']

    def __init__(self):
        super().__init__('FizzicsKey', 'Saniel')
        self._app = Fizzics()

    def reset_params(self):
        #TODO: What are the defualt values for these?
        self._app.set_object_property('view.JSContext.globalParameters', 'gravity_0', ('u', 0))
        self._app.set_object_property('view.JSContext.globalParameters', 'friction_0', ('u', 100))
        self._app.set_object_property('view.JSContext.globalParameters', 'collision_0', ('u', 0))

    def do_result_grav(self, result):
        if result:
            self._app.set_object_property('view.JSContext.globalParameters', 'gravity_0', ('u', 999))
        else:
            self._app.set_object_property('view.JSContext.globalParameters', 'gravity_0', ('u', 20))

    def do_result_fric(self, result):
        if result:
            self._app.set_object_property('view.JSContext.globalParameters', 'friction_0', ('u', 999))
        else:
            self._app.set_object_property('view.JSContext.globalParameters', 'friction_0', ('u', 0))


    def do_result_bounce(self, result):
        if result:
            self._app.set_object_property('view.JSContext.globalParameters', 'collision_0', ('u', 999))
        else:
            self._app.set_object_property('view.JSContext.globalParameters', 'collision_0', ('u', 0))


    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='DUMMY1')
        # get the player to the 'old' levels
        # disable tools
        self._app.disable_tool('fling')
        self._app.disable_tool('move')
        self._app.disable_tool('delete')
        return self.step_ingame

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_ingame(self):
        self.wait_confirm('DUMMY1')
        self.wait_confirm('DUMMY2')
        #return self.step_success
        return self.step_level1

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level1(self):
        #say puzzle
        #ask what grav
        #set grav
        #next level
        self._app.set_object_property('view.JSContext.globalParameters', 'gravity_0', ('u', 0))
        #for formatting and line length
        choice1 = ('CHOICEHIGH', self.do_result_grav, True)
        choice2 = ('CHOICELOW', self.do_result_grav, False)
        self.show_choices_message('SETGRAV', choice1, choice2).wait()
        self.wait_confirm('DUMMY3')
        self.reset_params()
        return self.step_level2
        



    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2(self):
        return self.step_level3



    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3(self):
        return self.step_success



    def step_success(self):
        self.wait_confirm('DUMMY3')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
