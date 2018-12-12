from eosclubhouse.utils import QS, QSH
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Roster(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Hackdex_chapter_one'
    SANIEL_CLICKED_KEY = 'app.com_endlessm_Hackdex_chapter_one.saniel_clicked'

    def __init__(self):
        super().__init__('Roster', 'ada', QS('ROSTER_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("OSIntro"):
            self.available = True

    def is_saniel_page_read(self):
        data = self.gss.get(self.SANIEL_CLICKED_KEY)
        if data is not None and data['clicked']:
            return True
        return False

    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                return self.step_explanation
            self.show_question(QS('ROSTER_PRELAUNCH'))
        if self.confirmed_step():
            return self.step_launch

    def step_launch(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message(QSH('ROSTER_LAUNCH'))
            Sound.play('quests/new-icon')
            Desktop.add_app_to_grid(self.TARGET_APP_DBUS_NAME)
            Desktop.show_app_grid()

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_delay1

    def step_delay1(self, time_in_step):
        if time_in_step > 2:
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            if self.is_saniel_page_read():
                return self.step_already_read
            Sound.play('quests/step-forward')
            self.show_hints_message(QSH('ROSTER_EXPLANATION'))

        if self.debug_skip():
            return self.step_success

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

        if self.is_saniel_page_read():
            return self.step_delay2

    def step_delay2(self, time_in_step):
        if time_in_step >= 2:
            return self.step_success

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('ROSTER_SUCCESS'))
        if self.confirmed_step():
            return self.step_end

    def step_already_read(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('ROSTER_ALREADYREAD'))
        if self.confirmed_step():
            return self.step_end

    def step_end(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            self.show_message(QS('ROSTER_END'), choices=[('Bye', self._confirm_step)])

        if self.confirmed_step():
            self.stop()

    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message(QS('ROSTER_ABORT'))

        if time_in_step > 5:
            self.stop()
