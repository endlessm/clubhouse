from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Roster(Quest):

    APP_NAME = 'com.endlessm.Hackdex_chapter_one'
    SANIEL_CLICKED_KEY = 'app.com_endlessm_Hackdex_chapter_one.saniel_clicked'

    def __init__(self):
        super().__init__('Roster', 'ada')
        self._app = App(self.APP_NAME)

    def is_saniel_page_read(self):
        data = self.gss.get(self.SANIEL_CLICKED_KEY)
        if data is not None and data['clicked']:
            return True
        return False

    def step_begin(self):
        if self._app.is_running():
            return self.step_explanation

        self.wait_confirm('PRELAUNCH')
        return self.step_launch

    def step_launch(self):
        self.show_hints_message('LAUNCH')
        Sound.play('quests/new-icon')
        Desktop.add_app_to_grid(self.APP_NAME)
        Desktop.focus_app(self.APP_NAME)

        self.wait_for_app_launch(self._app)
        self.pause(2)
        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        if self.is_saniel_page_read():
            return self.step_success, True

        Sound.play('quests/step-forward')
        self.show_hints_message('EXPLANATION')
        return self.step_wait_on_page_read

    @Quest.with_app_launched(APP_NAME)
    def step_wait_on_page_read(self):
        if self.is_saniel_page_read():
            self.pause(2)
            return self.step_success

        self.connect_gss_changes().wait()
        return self.step_wait_on_page_read

    def step_success(self, already_read=False):
        self.wait_confirm('ALREADYREAD' if already_read else 'SUCCESS')
        return self.step_end

    def step_end(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_message('END', choices=[('Bye', self.stop)])
