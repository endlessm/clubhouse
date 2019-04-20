from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Fizzics

class FizzicsKey(Quest):

    __available_after_completing_quests__ = ['MazePt3']

    def __init__(self):
        super().__init__('FizzicsKey', 'Saniel')
        self._app = Fizzics()

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
        self._app.set_object_property('view.JSContext.globalParameters', 'gravity_0', ('u', 0))
        self.wait_confirm('DUMMY1')
        self.wait_confirm('DUMMY2')
        #ask the player what they want
        #self.show_choices_message('SETFRIC', (('CHOICEHIGH', True), ('CHOICEHIGH', True))).wait()
        #unfreeze everything
        self._app.set_object_property('view.JSContext.globalParameters', 'gravity_0', ('u', 999))
        #if goal great
        #if not, reset time
        return self.step_success

    def step_success(self):
        self.wait_confirm('DUMMY3')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
