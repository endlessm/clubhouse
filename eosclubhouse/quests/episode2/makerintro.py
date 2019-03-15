from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class MakerIntro(Quest):

    APP_NAME = 'com.endlessm.Fizzics'
    GAME_PRESET = 1001

    __available_after_completing_quests__ = ['Investigation']

    def __init__(self):
        super().__init__('MakerIntro', 'faber')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        self.show_hints_message('EXPLANATION')
        self._app.set_js_property('preset', ('i', self.GAME_PRESET))
        return self.step_checkgoal

    @Quest.with_app_launched(APP_NAME)
    def step_checkgoal(self):
        if not self._app.get_js_property('quest1Success'):
            self.wait_for_app_js_props_changed(self._app, ['quest1Success', 'flingCount'])

        if self._app.get_js_property('flingCount', 0) > 0:
            self.show_hints_message('FLING')
            return self.step_fling

        return self.step_success

    @Quest.with_app_launched(APP_NAME)
    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.wait_confirm('WHATISIT')
        self.wait_confirm('GIVEITEM')
        self.gss.set("item.key.unknown_item", {'used': True, 'consume_after_use': True})
        self.give_item('item.stealth.1')
        self.wait_confirm('STEALTHQUESTION')
        self.wait_confirm('STEALTHEXPLANATION')
        return self.step_thanks

    @Quest.with_app_launched(APP_NAME)
    def step_fling(self):
        if self._app.get_js_property('flingCount') == 0:
            self.show_hints_message('EXPLANATION')
            return self.step_checkgoal
        self.wait_for_app_js_props_changed(self._app, ['flingCount'])
        return self.step_fling

    def step_thanks(self):
        Sound.play('quests/quest-complete')
        self.show_confirm_message('THANKS', confirm_label='Bye').wait()

        self.complete = True
        self.available = False

        self.stop()
