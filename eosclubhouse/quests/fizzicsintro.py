from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class FizzicsIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'

    def __init__(self):
        super().__init__('Fizzics Intro', 'ada', QS('FIZZICSINTRO_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._hintIndex = -1
        self._hints = []
        self._hint_character_id = None

        if not self.conf.get('complete', False):
            self.highlighted = True

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
        self.show_next_hint()

    def show_next_hint(self):
        if self._hintIndex >= len(self._hints) - 1 or self._hintIndex < 0:
            self._hintIndex = 0
            label = "Give me a hint"
        else:
            self._hintIndex += 1
            if self._hintIndex == len(self._hints) - 1:
                label = "What's my goal?"
            else:
                label = "I'd like another hint"
        self.show_message(self._hints[self._hintIndex], choices=[(label, self.show_next_hint)],
                          character_id=self._hint_character_id)

    def get_current_level(self):
        try:
            level = self._app.get_object_property('view.JSContext.globalParameters', 'currentLevel')
            return level
        except Exception as ex:
            print(ex)
        return -1

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                return self.step_explanation
            self.set_hints('FIZZICSINTRO_LAUNCH')
            Desktop.show_app_grid()

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME) or self.debug_skip():
            return self.step_delay1

    def step_delay1(self, time_in_step):
        if time_in_step > 2:
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICSINTRO_EXPLANATION'))

        if self.confirmed_step():
                return self.step_level1
        if self.get_current_level() >= 1:
            return self.step_level2
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_level1(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('FIZZICSINTRO_LEVEL1')

        if self.get_current_level() >= 1:
            return self.step_level2
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_level2(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('FIZZICSINTRO_LEVEL2')

        if self.get_current_level() >= 2:
            return self.step_success
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICSINTRO_SUCCESS'))
        if self.confirmed_step():
            return self.step_ricky

    def step_ricky(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/riley-intro')
            self.show_question(QS('FIZZICSINTRO_RICKY'), character_id='ricky')
        if self.confirmed_step():
            return self.step_intro

    def step_intro(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICSINTRO_INTRO'))
        if self.confirmed_step():
            return self.step_prekey

    def step_prekey(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('FIZZICSINTRO_KEY'))
        if self.confirmed_step():
            return self.step_key

    def step_key(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            self.give_item('item.key.fizzics.1')
            self.show_question(QS('FIZZICSINTRO_END'))
            Sound.play('quests/quest-complete')
        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICSINTRO_ABORT'))

        if time_in_step > 5:
            self.stop()
