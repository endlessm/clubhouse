from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, Quest
from eosclubhouse.system import Desktop, App, Sound


class OSIntro(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.OperatingSystemApp'

    def __init__(self):
        super().__init__('OS Intro', 'ada', QS('OSINTRO_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._current_step = None
        self._clicked = False

    # STEP 0
    def step_first(self, time_in_step):
        if time_in_step == 0:
            self._current_step = None
            self._clicked = False
            self.show_question('OSINTRO_PRELAUNCH')

        if self.confirmed_step():
            return self.step_launch

    def step_launch(self, time_in_step):
        if time_in_step == 0:
            self.show_hints_message('OSINTRO_LAUNCH')
            Sound.play('quests/new-icon')
            Desktop.add_app_to_grid(self.TARGET_APP_DBUS_NAME)
            Desktop.focus_app(self.TARGET_APP_DBUS_NAME)

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_explanation

    def step_explanation(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/step-forward')
            self.show_question('OSINTRO_EXPLANATION')

        if self.confirmed_step():
            return self.step_saniel
        try:
            if self._app.get_js_property('flipped'):
                return self.step_saniel_flip
            if not self._clicked and self._app.get_js_property('clicked'):
                self.show_question('OSINTRO_CLICK')
                self._clicked = True
            elif self._clicked and not self._app.get_js_property('clicked'):
                self.show_question('OSINTRO_EXPLANATION')
                self._clicked = False
        except Exception as e:
            print(e)
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_saniel(self, time_in_step):
        if time_in_step == 0:
            self.show_question('OSINTRO_SANIEL')

        if self.confirmed_step():
            return self.step_intro
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        try:
            if self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                self._current_step = self.step_saniel
                return self.step_flipped
        except Exception as e:
            print(e)

    def step_saniel_flip(self, time_in_step):
        if time_in_step == 0:
            Sound.play('quests/saniel-angry')
            self.show_hints_message('OSINTRO_SANIEL_FLIP')

        try:
            if not self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                return self.step_intro
        except Exception as e:
            print(e)
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_intro(self, time_in_step):
        if time_in_step == 0:
            self.show_question('OSINTRO_INTRO')

        if self.confirmed_step():
            return self.step_saniel2
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        try:
            if self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                self._current_step = self.step_intro
                return self.step_flipped
        except Exception as e:
            print(e)

    def step_saniel2(self, time_in_step):
        if time_in_step == 0:
            self.show_question('OSINTRO_SANIEL2')

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
                self._current_step = self.step_saniel2
                return self.step_flipped
        except Exception as e:
            print(e)

    def step_wrapup(self, time_in_step):
        if time_in_step == 0:
            self.show_question('OSINTRO_WRAPUP')

            # this is the quest that makes Saniel appear
            saniel_questset = Registry.get_quest_set_by_name('SanielQuestSet')
            if saniel_questset is not None:
                saniel_questset.visible = True

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
            Sound.play('quests/saniel-angry')
            self.show_hints_message('OSINTRO_FLIPPED')
        try:
            if not self._app.get_object_property('view.JSContext.globalParameters', 'flipped'):
                return self._current_step
        except Exception as e:
            print(e)

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message('OSINTRO_ABORT')

        if time_in_step > 5:
            self.stop()
