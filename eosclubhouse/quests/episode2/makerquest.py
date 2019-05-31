from eosclubhouse.apps import Fizzics
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class MakerQuest(Quest):

    GAME_PRESET = 1002

    __items_on_completion__ = {'item.stealth.3': {'consume_after_use': True}}

    def setup(self):
        self._app = Fizzics()

    def step_begin(self):
        self.ask_for_app_launch(self._app)

        self._app.set_js_property('preset', ('i', self.GAME_PRESET))
        self.show_hints_message('EXPLANATION')
        return self.step_explanation

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_explanation(self):
        if not self._app.get_js_property('quest2Success') and not self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['quest2Success'])

        self.wait_confirm('SUCCESS')
        self.give_item('item.stealth.3', consume_after_use=True)
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
