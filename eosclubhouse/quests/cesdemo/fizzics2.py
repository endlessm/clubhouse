from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class Fizzics2(Quest):

    __complete_episode__ = True

    APP_NAME = 'com.endlessm.Fizzics'
    GAME_PRESET = 1000

    def __init__(self):
        super().__init__('Fizzics 2', 'riley')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_set_level

    @Quest.with_app_launched(APP_NAME)
    def step_alreadyrunning(self):
        self.wait_confirm('ALREADY_RUNNING')
        return self.step_set_level

    @Quest.with_app_launched(APP_NAME)
    def step_set_level(self):
        self._app.set_js_property('preset', ('i', self.GAME_PRESET))

        Sound.play('quests/step-forward')
        self.show_hints_message('GOAL')
        return self.step_wait_for_success

    @Quest.with_app_launched(APP_NAME)
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
        self.give_item('item.key.fizzics.2')
        Sound.play('quests/quest-complete')

        self.wait_confirm('END')
        self.stop()
