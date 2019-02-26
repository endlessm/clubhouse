from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class Chore(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('Chore', 'saniel')
        self._app = App(self.APP_NAME)
        self.available = False
        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete('Intro'):
            self.available = True

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        # @todo: Add steps in between, since the we've waited for the app to be launched but
        # step_end doesn't depend on the app being running.
        return self.step_explanation

    def step_explanation(self):
        self.show_confirm_message('EXPLANATION').wait()
        return self.step_key

    def step_key(self):
        self.show_confirm_message('KEY').wait()
        return self.step_end

    def step_end(self):
        self.give_item('item.key.unknown_item', "You've received an unknown item",
                       consume_after_use=True)
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
