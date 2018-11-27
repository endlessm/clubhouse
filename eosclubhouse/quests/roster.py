from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Roster(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Hackdex_chapter_one'

    def __init__(self):
        super().__init__('Roster', 'ada', QS('ROSTER_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._hintIndex = -1
        self._hints = []
        self._hint_character_id = None

    # TODO: Fold all the hints stuff into the base class if we go with this
    def set_hints(self, dialog_id, character_id=None):
        self._hintIndex = -1
        self._hints = [QS(dialog_id)]
        self._hint_character_id = character_id
        hintIndex = 0
        while True:
            hintIndex += 1
            hintId = dialog_id + '_HINT' + str(hintIndex)
            hintStr = QS(hintId)
            if hintStr is None:
                break
            self._hints.append(hintStr)
        self.show_hint()

    def show_hint(self):
        label = 'Hint'
        if self._hintIndex >= len(self._hints) - 1:
            self._hintIndex = 0
        else:
            self._hintIndex += 1
            if self._hintIndex == len(self._hints) - 1:
                label = 'Goal'
        self.show_message(self._hints[self._hintIndex], choices=[(label, self.show_hint)],
                          character_id=self._hint_character_id)

    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                return self.step_explanation
            self.show_question(QS('ROSTER_PRELAUNCH'))
        if self.confirmed_step():
            return self.step_launch

    def step_launch(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('ROSTER_LAUNCH')
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
            self.set_hints('ROSTER_EXPLANATION')

        if time_in_step < 2:
            return

        # TODO: Check for reading history visiting archivist. Right now moving on after 15 sec.
        if time_in_step > 15:
            return self.step_success

        if self.debug_skip():
            return self.step_success

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            self.show_question(QS('ROSTER_SUCCESS'))

        if self.confirmed_step():
            self.stop()

    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('ROSTER_ABORT'))

        if time_in_step > 5:
            self.stop()
