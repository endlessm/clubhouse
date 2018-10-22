import time

from gi.repository import GLib
from eosclubhouse.libquest import Quest
from eosclubhouse.desktop import Desktop, App


class HackyBalls0(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.hackyballs'

    def __init__(self):
        super().__init__('Hacky Balls 0', 'teacher',
                         "Let's try doing our first physics experiment.")
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._hint0 = False
        self._hint1 = False
        self._hintCount = False
        self._initialized = False
        self._msg = ""

    def start(self):
        self.set_keyboard_request(True)

        dt = 1
        time_in_step = 0
        starting = True
        step_func = self.step_first

        while True:
            new_func = step_func(step_func, starting, time_in_step)
            if new_func is None:
                break
            elif new_func != step_func:
                step_func = new_func
                time_in_step = 0
                starting = True
            else:
                time.sleep(dt)
                time_in_step += dt
                starting = False

    # STEP 0
    def step_first(self, step, starting, time_in_step):
        if starting:
            self.show_message("Glad you could join me. Launch the Hacky Balls app and "
                              "let's get started with the experiment.")

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_wait_score

        if (time_in_step > 20 and not self._hint0):
            self.show_message("Start by launching the Hacky Balls app on the desktop.")
            self._hint0 = True

        return step

    # STEP 1
    def step_wait_score(self, step, starting, time_in_step):
        if starting:
            self._msg = "For this experiment, we need to have 20 red balls at once, " \
                        "but they can't touch each other."
            self.show_message(self._msg)

        if time_in_step < 3:
            return step

        try:
            if not self._initialized:
                self._app.set_object_property('view.JSContext.globalParameters',
                                              'preset',
                                              GLib.Variant('i', 11))
                self._initialized = True
            else:
                if self._app.get_object_property('view.JSContext.globalParameters',
                                                 'quest0Success'):
                    return self.step_reward

                type1BallCount = self._app.get_object_property('view.JSContext.globalParameters',
                                                               'type1BallCount')
                if (type1BallCount < 20 and not self._hintCount):
                    self.show_message("You need to have at least 20 red balls "
                                      "for this experiment.")
                    self._hintCount = True
                elif (type1BallCount >= 20 and self._hintCount):
                    self.show_message(self._msg)
                    self._hintCount = False
                elif (time_in_step > 60 and not self._hint1):
                    self._msg = "The red balls are constantly touching each other. " \
                                "If they took less space... Try to get them not to touch."
                    self.show_message(self._msg)
                    self._hint1 = True
        except Exception as ex:
            print(ex)

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_end_no_app

        return step

    # STEP 2
    def step_reward(self, step, starting, time_in_step):
        if starting:
            self.show_message("Excellent! I see you found one way to do that. "
                              "Come talk to me in the Clubhouse if you want to "
                              "perform some more experiments.")

        if time_in_step > 10:
            return

        return step

    # STEP Abort
    def step_end_no_app(self, step, starting, time_in_step):
        if starting:
            self.show_message("We can do it another time. Come talk to me in the Clubhouse "
                              "whenever you're ready.")

        if time_in_step > 5:
            return

        return step


class HackyBalls1(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.hackyballs'

    def __init__(self):
        super().__init__('Hacky Balls 1', 'teacher',
                         "Are you ready for some physics experiments?")
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._hint0 = False
        self._hint1 = False
        self._initialized = False

    def start(self):
        self.set_keyboard_request(True)

        dt = 1
        time_in_step = 0
        starting = True
        step_func = self.step_first

        while True:
            new_func = step_func(step_func, starting, time_in_step)
            if new_func is None:
                break
            elif new_func != step_func:
                step_func = new_func
                time_in_step = 0
                starting = True
            else:
                time.sleep(dt)
                time_in_step += dt
                starting = False

    # STEP 0
    def step_first(self, step, starting, time_in_step):
        if starting:
            self.show_message("Good. Launch the Hacky Balls app. Your goal "
                              "is to make it so 10 green balls are touching "
                              "a single red ball at once.")

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_wait_score

        if (time_in_step > 20 and not self._hint0):
            self.show_message("Start by launching the Hacky Balls app on the desktop.")
            self._hint0 = True

        return step

    # STEP 1
    def step_wait_score(self, step, starting, time_in_step):
        if starting:
            self.show_message("Now see if you can set things up so 10 green balls "
                              "are touching a single red ball at the same time.")

        try:
            if not self._initialized:
                self._app.set_object_property('view.JSContext.globalParameters',
                                              'preset', GLib.Variant('i', 3))
                self._initialized = True
            elif self._app.get_object_property('view.JSContext.globalParameters', 'quest1Success'):
                return self.step_reward
        except Exception as ex:
            print(ex)

        if time_in_step > 60 and not self._hint1:
            self.show_message("Clearly stacking them up isn't going to work. Try hacking "
                              "the app and changing the forces between ball types.")
            self._hint1 = True

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_end_no_app

        return step

    # STEP 2
    def step_reward(self, step, starting, time_in_step):
        if starting:
            self.show_message("Good job! That's the way to do it. We'll come back later to "
                              "try other experiements.")

        if time_in_step > 10:
            return

        return step

    # STEP Abort
    def step_end_no_app(self, step, starting, time_in_step):
        if starting:
            self.show_message("We can do it another time. Come talk to me in the Clubhouse "
                              "whenever you're ready.")

        if time_in_step > 5:
            return

        return step

