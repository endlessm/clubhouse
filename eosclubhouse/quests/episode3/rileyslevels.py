from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class RileysLevels(Quest):

    APP_NAME = 'com.endlessm.Fizzics'

    __available_after_completing_quests__ = ['SetUp']

    def __init__(self):
        super().__init__('RileysLevels', 'ada')
        self._app = App(self.APP_NAME)

    def _at_level_11(self):
        return False

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_explain

    @Quest.with_app_launched(APP_NAME)
    def step_explain(self):
        self.wait_confirm('GETTOLEVEL11')
        self.show_hints_message('LEVEL11')
        while not (self._at_level_11() or self.debug_skip()) and not self.is_cancelled():
            self.connect_app_js_props_changes(self._app,
                                              ['currentLevel', 'levelSuccess']).wait()

        self.wait_confirm('LEVEL12')
        self.wait_confirm('NOMOVING')
        return self.step_success

    def step_success(self):
        self.give_item('item.program.1')
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
