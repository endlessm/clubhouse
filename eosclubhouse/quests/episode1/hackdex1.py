from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class Hackdex1(Quest):

    APP_NAME = 'com.endlessm.Hackdex_chapter_one'

    __available_after_completing_quests__ = ['BreakSomething', 'Roster']

    def __init__(self):
        self._is_corrupt_setup = False

        super().__init__('Hackdex Corruption', 'saniel')
        self._app = App(self.APP_NAME)

    def update_availability(self, _gss=None):
        super().update_availability()

        if self._is_corrupt_setup:
            return

        # We override this method just so we set the Hackdex corruption state when the quest
        # becomes available.
        if self.available:
            if not self._app_is_corrupted():
                self.gss.set('app.com_endlessm_Hackdex_chapter_one.corruption',
                             {'state': 'corrupted', 'color': ''})
            self._is_corrupt_setup = True

    def _app_is_corrupted(self):
        data = self.gss.get('app.com_endlessm_Hackdex_chapter_one.corruption', {'state': None})
        return data.get('state') == 'corrupted'

    def step_begin(self):
        self.wait_confirm('PRELAUNCH')
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        Sound.play('quests/step-forward')
        self.show_hints_message('GOAL')
        return self.step_check_unlock

    @Quest.with_app_launched(APP_NAME)
    def step_check_unlock(self):
        # Check unlock level 1
        item = self.gss.get('item.key.hackdex1.1')
        if item is not None and item.get('used', False):
            Sound.play('quests/step-forward')
            self.show_hints_message('UNLOCKED')
            return self.step_check_goal

        self.connect_gss_changes().wait()
        return self.step_check_unlock

    def step_check_goal(self):
        if not self._app.is_running():
            return self.abort

        # Check for color change
        data = self.gss.get('app.com_endlessm_Hackdex_chapter_one.corruption')
        if data is None:
            return self.abort

        if data['state'] == 'fixed' or self.debug_skip():
            self.pause(2)
            return self.step_success

        # The HackDex app is restarted when its parameters are changed and the app is flipped
        # back, so we check that and give it time before considering it has stopped running.
        self.connect_app_quit(self._app).wait()
        self.wait_for_app_launch(self._app, timeout=2)

        return self.step_check_goal

    def step_success(self):
        Sound.play('quests/step-forward')
        self.show_confirm_message('SUCCESS', confirm_label='OK').wait()

        self.give_item('item.key.fizzics.2')
        self.complete = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.wait_confirm('AFTERKEY')

        self.stop()
