from eosclubhouse.utils import QS, QSH
from eosclubhouse.libquest import Registry, Quest
from eosclubhouse.system import Desktop, App, Sound


class OSIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('OS Intro', 'ada', QS('OSINTRO_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._current_step = None

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self.show_question(QS('OSINTRO_PRELAUNCH'))

        if self.confirmed_step():
            return self.step_launch

    def step_launch(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message(QSH('OSINTRO_LAUNCH'))
            Sound.play('quests/new-icon')
            Desktop.add_app_to_grid(self.TARGET_APP_DBUS_NAME)
            Desktop.show_app_grid()

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
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
            Sound.play('quests/archivist-intro')
            self.show_question(QS('OSINTRO_ARCHIVIST'), character_id='archivist')

        if self.confirmed_step():
            return self.step_intro
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        try:
            if self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                self._current_step = self.step_archivist
                return self.step_flipped
        except Exception as e:
            print(e)

    def step_archivist_flip(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/archivist-angry')
            self.show_hints_message(QSH('OSINTRO_ARCHIVIST_FLIP'), character_id='archivist')

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
            Sound.play('quests/archivist-angry')
            self.show_hints_message(QSH('OSINTRO_FLIPPED'), character_id='archivist')
        try:
            if not self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                return self._current_step
        except Exception as e:
            print(e)

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/quest-aborted')
            self.show_message(QS('OSINTRO_ABORT'))

        if time_in_step > 5:
            self.stop()
