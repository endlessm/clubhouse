from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class MakerIntro(Quest):

    APP_NAME = 'com.endlessm.Fizzics'
    GAME_PRESET = 1001

    def __init__(self):
        super().__init__('MakerIntro', 'faber')
        self.available = False
        self._app = App(self.APP_NAME)

        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete('Investigation'):
            self.available = True

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self.show_hints_message('EXPLANATION')
        self._app.set_js_property('preset', ('i', self.GAME_PRESET))
        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        if self._app.get_js_property('quest1Success') or self.debug_skip():
            self.wait_confirm('SUCCESS')
            self.wait_confirm('WHATISIT')
            self.wait_confirm('GIVEITEM')
            self.gss.set("item.key.unknown_item", {'used': True, 'consume_after_use': True})
            self.give_item('item.stealth.4')
            self.wait_confirm('STEALTHQUESTION')
            self.wait_confirm('STEALTHEXPLANATION')
            return self.step_thanks

        self.wait_for_app_js_props_changed(self._app, ['quest1Success'])
        return self.step_explanation

    def step_thanks(self):
        Sound.play('quests/quest-complete')
        self.show_confirm_message('THANKS', confirm_label='Bye').wait()

        self.conf['complete'] = True
        self.available = False

        self.stop()
