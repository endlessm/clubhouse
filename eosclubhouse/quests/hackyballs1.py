
from gi.repository import Gdk, Gio, GLib
from eosclubhouse.libquest import Registry, Quest, QuestSet
from eosclubhouse.desktop import Desktop, App


class HackyBalls1(Quest):

    TARGET_APP_DBUS_NAME = 'com.endlessm.hackyballs'


    def __init__(self):
        super().__init__('Hacky Balls 1', 'teacher',
                         'Are you ready for some physics experiments?')
        self._app = App(self.TARGET_APP_DBUS_NAME)
        self._hint0 = False
        self._hint1 = False
        self._initialized = False



    ### STEP 0
    def step_first(self, step, starting, time_in_step):
        if starting:
            self.show_message("Good. Launch the Hacky Balls app. Your goal is to make it so 8 green balls are touching a single red ball at once.")

        if Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_wait_score

        if (time_in_step > 20 and not self._hint0):
            self.show_message("Start by launching the Hacky Balls app on the desktop.")
            self._hint0 = True

        return step


    ### STEP 1
    def step_wait_score(self, step, starting, time_in_step):
        if starting:
            self.show_message("Now see if you can set things up so 8 green balls are touching a single red ball at the same time.")

        try:
            if not self._initialized:
                print("Starting to initialize...")
                # Maybe set preset scenario here
                #self._app.set_object_property('label_name', 'label', GLib.Variant('s','Ricky'))
                #elf._app.set_object_property('label_score', 'label', GLib.Variant('s',str(score_to_beat)))
                self._initialized = True
                print("Initialized")
            elif self.debug_was_key_pressed() or self._app.get_object_property('view_hack', 'goal1'):
                return self.step_reward
        except Exception as ex:
            print("Exception!")
            print(ex)

        if time_in_step > 60 and not self._hint1:
            self.show_message("Clearly stacking them up isn't going to work. Try hacking the app and changing the forces between ball types.")
            self._hint1 = True

        if not Desktop.app_is_running(self.TARGET_APP_DBUS_NAME):
            return self.step_end_no_app

        return step


    ### STEP 2
    def step_reward(self, step, starting, time_in_step):
        if starting:
            self.show_message("Good job! That's the way to do it. We'll come back later to try other experiements.")
 
        if time_in_step > 10:
            return

        return step


    ### STEP Abort
    def step_end_no_app(self, step, starting, time_in_step):
        if starting:
            self.show_message("We can do it another time. Come talk to me in the Clubhouse whenever you're ready.")
 
        if time_in_step > 5:
            return

        return step


