from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class Hackdex2Decrypt(Quest):

    APP_NAME = 'com.endlessm.Hackdex2'

    def __init__(self):
        super().__init__('Hackdex2Decrypt', 'riley')
        self._app = App(self.APP_NAME)

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        return self.step_explanation

    # @todo: Set as needing the app to be running (we cannot add it yet since the app doesn't exist)
    def step_explanation(self):
        self.show_hints_message('EXPLANATION')

        # @todo: Check for FtH (the app used here doesn't exist so we cannot even wait for
        # phony properties on it, and thus pause instead just for the debug).
        while not (self.debug_skip() or self.is_cancelled()):
            self.pause(3600)

        return self.step_hack

    # @todo: Set as needing the app to be running (we cannot add it yet since the app doesn't exist)
    def step_hack(self):
        self.show_hints_message('HACK')

        # @todo: The app used here doesn't exist so we cannot even wait for phony properties on it,
        # and thus pause instead just for the debug.
        while not (self.debug_skip() or self.is_cancelled()):
            self.pause(3600)

        return self.step_success

    def step_success(self):
        self.conf['complete'] = True
        self.available = False

        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()

        if self.confirmed_step():
            Sound.play('quests/quest-complete')

        self.stop()
