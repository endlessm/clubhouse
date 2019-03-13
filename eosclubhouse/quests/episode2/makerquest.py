from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class MakerQuest(Quest):

    APP_NAME = 'com.endlessm.Fizzics'
    GAME_PRESET = 1002

    def __init__(self):
        super().__init__('MakerQuest', 'faber')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self._app.set_js_property('preset', ('i', self.GAME_PRESET))
        self.show_hints_message('EXPLANATION')
        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        if not self._app.get_js_property('quest2Success') and not self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['quest2Success'])

        self.wait_confirm('SUCCESS')
        self.give_item('item.stealth.3')
        return self.step_end

    def step_end(self):
        self.conf['complete'] = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
