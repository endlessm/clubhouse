from eosclubhouse.apps import Fizzics
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Fizzics2(Quest):

    __items_on_completion__ = {'item.key.hackdex1.1': {}}

    GAME_PRESET = 1000

    def __init__(self):
        super().__init__('Fizzics 2', 'riley')
        self._app = Fizzics()

    def step_begin(self):
        if self._app.is_running():
            return self.step_alreadyrunning

        self.ask_for_app_launch(self._app)
        return self.step_set_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_alreadyrunning(self):
        self.wait_confirm('ALREADY_RUNNING')
        return self.step_set_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_set_level(self):
        self._app.set_js_property('preset', ('i', self.GAME_PRESET))

        Sound.play('quests/step-forward')
        self.show_hints_message('GOAL')
        return self.step_wait_for_success

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_wait_for_success(self):
        if self._app.get_js_property('quest0Success'):
            return self.step_success

        self.wait_for_app_js_props_changed(self._app, ['quest0Success'])
        return self.step_wait_for_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.wait_confirm('REWARD')
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
        self.give_item('item.key.hackdex1.1')
        Sound.play('quests/quest-complete')

        self.wait_confirm('END')
        self.stop()
