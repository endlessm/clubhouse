from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, Quest
from eosclubhouse.system import Desktop, App, Sound


class OSIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('OS Intro', 'ada', QS('OSINTRO_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._current_step = None
        self._hintIndex = -1
        self._hints = []
        self._hint_character_id = None

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

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_PRELAUNCH'))

        if self.confirmed_step():
            return self.step_launch

    def step_launch(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('OSINTRO_LAUNCH')
            Sound.play('quests/new-icon')
            Desktop.add_app_to_grid(self.TARGET_APP_DBUS_NAME)
            Desktop.show_app_grid()

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_EXPLANATION'))

        if self.confirmed_step():
            return self.step_archivist
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        try:
            if self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                return self.step_archivist_flip
            if self._app.get_object_property('view.JSContext.globalParameters', 'clicked'):
                self.show_question(QS('OSINTRO_CLICK'))
        except Exception as e:
            print(e)

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_archivist(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_ARCHIVIST'), character_id='archivist')

        if self.confirmed_step():
            return self.step_intro
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_archivist_flip(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('OSINTRO_ARCHIVIST_FLIP', character_id='archivist')

        try:
            if not self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                return self.step_intro
        except Exception as e:
            print(e)
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_intro(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_INTRO'))

        if self.confirmed_step():
            return self.step_archivist2
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        try:
            if self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                self._current_step = self.step_intro
                return self.step_flipped
        except Exception as e:
            print(e)

    def step_archivist2(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_ARCHIVIST2'), character_id='archivist')

        if self.confirmed_step():
            # We're putting this here to avoid getting multiple sounds in the last step
            # as they flip to the other side.
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            return self.step_wrapup
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        try:
            if self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                self._current_step = self.step_archivist2
                return self.step_flipped
        except Exception as e:
            print(e)

    def step_wrapup(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_WRAPUP'))

            # this is the quest that makes the Archivist appear
            archivist_questset = Registry.get_quest_set_by_name('ArchivistQuestSet')
            if archivist_questset is not None:
                archivist_questset.visible = True
                archivist_questset.nudge()

        try:
            if self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                self._current_step = self.step_wrapup
                return self.step_flipped
        except Exception as e:
            print(e)

        if self.confirmed_step():
            self.stop()

    def step_flipped(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('OSINTRO_FLIPPED', character_id='archivist')
        try:
            if not self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                return self._current_step
        except Exception as e:
            print(e)

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('OSINTRO_ABORT'))

        if time_in_step > 5:
            self.stop()
