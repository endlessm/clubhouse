from eosclubhouse.utils import QS
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class Fizzics1(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.Fizzics'
    APP_JS_PARAMS = 'view.JSContext.globalParameters'

    def __init__(self):
        super().__init__('Fizzics 1', 'ricky', QS('FIZZICS1_QUESTION'))
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self.gss.connect('changed', self.update_availability)
        self.available = False
        self.update_availability()
        self._hintIndex = -1
        self._hints = []
        self._hint_character_id = None

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("FizzicsIntro"):
            self.available = True

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
            if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
                self.set_hints('FIZZICS1_LAUNCH')
                Desktop.show_app_grid()
            else:
                return self.step_delay1

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_delay1

    def step_delay1(self, time_in_step):
        if time_in_step > 2:
            return self.step_goal

    def step_goal(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('FIZZICS1_GOAL')

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

        try:
            if self._app.get_object_property(self.APP_JS_PARAMS,
                                             'currentLevel') == 7:
                return self.step_level8
        except Exception as ex:
            print(ex)

    def step_backtolevel8(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICS1_BACKTOLEVEL8'))

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort
        try:
            if self._app.get_object_property(self.APP_JS_PARAMS,
                                             'currentLevel') == 7:
                return self.step_level8
        except Exception as ex:
            print(ex)

    def step_level8(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('FIZZICS1_LEVEL8')

        try:
            # Check for flipping the app
            if self._app.get_object_property(self.APP_JS_PARAMS, 'flipped'):
                return self.step_flipped
            # Check if they're going to another level
            if self._app.get_object_property(self.APP_JS_PARAMS,
                                             'currentLevel') != 7:
                return self.step_backtolevel8
            # Check for success
            if self._app.get_object_property(self.APP_JS_PARAMS, 'currentLevel') == 8 or \
               self._app.get_object_property(self.APP_JS_PARAMS, 'levelSuccess'):
                return self.step_success
            if self._app.get_object_property(self.APP_JS_PARAMS,
                                             'currentLevel') < 7:
                return self.step_backtolevel8
        except Exception as ex:
            print(ex)

        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_flipped(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('FIZZICS1_FLIPPED')

        # Wait until they unlock the panel
        try:
            item = self.gss.get('item.key.fizzics.1')
            if item is not None and item.get('used', False):
                return self.step_hack
            # Check for flipping back
            if not self._app.get_object_property(self.APP_JS_PARAMS, 'flipped'):
                return self.step_level8
        except Exception as ex:
            print(ex)

        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_hack(self, time_in_step):
        if time_in_step == 0:
            self.set_hints('FIZZICS1_HACK')

        try:
            # Check for success
            if self._app.get_object_property(self.APP_JS_PARAMS, 'currentLevel') == 8 or \
               self._app.get_object_property(self.APP_JS_PARAMS, 'levelSuccess'):
                return self.step_success
            # Check for going to another level
            if self._app.get_object_property(self.APP_JS_PARAMS,
                                             'currentLevel') < 7:
                return self.step_backtolevel8
        except Exception as ex:
            print(ex)
        # Check for abandoning the app
        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_abort

    def step_success(self, time_in_step):
        if time_in_step == 0:
            self.conf['complete'] = True
            self.available = False
            Sound.play('quests/quest-complete')
            self.show_question(QS('FIZZICS1_SUCCESS'))

        if self.confirmed_step():
            self.stop()

    # STEP Abort
    def step_abort(self, time_in_step):
        if time_in_step == 0:
            self.show_message(QS('FIZZICS1_ABORT'))

        if time_in_step > 5:
            self.stop()
