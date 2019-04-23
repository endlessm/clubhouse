# from eosclubhouse.apps import Maze
from eosclubhouse.apps import Fizzics  # just for testing
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class MazePt1(Quest):

    def __init__(self):
        super().__init__('MazePt1', 'riley')
        # MazePt1 is the class we are defining rn, and riley is the current character
        # In this case, super() calls __init__() in the parent class (the constructor)...
        # ...but super() is a special case in Python that doesn't work how you would expect it to.
        # Try to avoid using it if you can.
        # Here, this call is functionally identical to Quest().__init__()
        # self._app = Maze()
        # self is the same as C#'s keyword this
        # using _ (underscore) means it's a class internal variable.
        # Maze() calls the constructor of the Maze class - now _app refers to that instance of Maze.
        # This allows us to call hooks from that app (which are defined in ../apps.py)
        self._app = Fizzics()
        # for testing the app, since the maze hooks aren't in yet

    def step_begin(self):
        self.wait_confirm('TRANSFER')
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH_ADA')
        # wait for the user to launch the app
        # this method will present the message._id dialog, and go away
        # once self._app has launched, and it will also highlight the icon on the desktop.
        # if there is LAUNCH_ADA_HINT1, then it will also use that.
        return self.step_play_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_play_level(self):
        current_level = self._app.get_current_level()
        # when the user launches the app:
        # Riley says MAZEPT1_MANUAL1 which has MAZEPT1_MANUAL1_HINT1 _HINT2 and _HINT3
        if current_level >= 1:  # should be == when rileymaze hooks get in
            self.show_hints_message('MANUAL1')
            # show_hints_message() differs from wait_confirm() in that it operates asynchronously
            # it doesn't block downstream steps if the user doesn't click on it.
            # also, it loops through a set of messages: the _HINT# variations,
            # and then asks "what is my goal?" before restarting
        # self.wait_for_app_js_props_changed(self._app, ['level'])
        self.pause(7)
        # return self.step_level2
        # return self.step_success
        # and now we move on to the end of the quest step

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2(self):
        # at the start of level 2, Riley says MAZEPT1_MANUAL2
        self.wait_confirm('MANUAL2')
        return self.step_level3
        # if we ever restart a level whose #<X (see below) because the user lost, Riley plays
        # MAZEPT1_DIED_RESTART

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3(self):
        # at the start of level 3, Saniel says MAZEPT1_MANUAL3
        self.wait_confirm('MANUAL3')
        return self.step_levelx

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_levelx(self):
        # at the start of level #(tbd), Saniel says MAZEPT1_MANUAL4 which has _HINT1
        self.show_hints_message('MANUAL4')
        return self.step_levely

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_levely(self):
        # at the start of level #(tbd), Riley says MAZEPT1_AUTO1
        # then Felix says MAZEPT1_AUTO1_FELIX
        # then Faber says MAZEPT1_AUTO1_FABER
        # then Ada says MAZEPT1_AUTO1_ADA
        # then Riley says MAZEPT1_AUTO1_RILEY
        # then Saniel says MAZEPT1_AUTO1_SANIEL which has _HINT1
        self.wait_confirm('AUTO1')
        # self.wait_confirm('AUTO1_FELIX')
        self.wait_confirm('AUTO1_FABER')
        self.wait_confirm('AUTO1_ADA')
        self.wait_confirm('AUTO1_RILEY')
        self.show_hints_message('AUTO1_SANIEL')
        self.pause(7)
        self.show_hints_message('AUTO2')
        self.pause(7)
        self.show_hints_message('AUTO3')
        self.wait_confirm('AUTO4')
        self.wait_confirm('AUTO5')
        self.show_hints_message('AUTO5_ADA')
        self.pause(7)
        return self.step_success

    # at the start of level X(tbd), Saniel says MAZEPT1_AUTO2 which has _HINT1

    # at the start of level X+1, Saniel says MAZEPT1_AUTO3 which has _HINT1 and _HINT2
    # if we restart this level because the user lost, Saniel says MAZEPT1_AUTO3_FAILURE
    # if the player finishes this level successfully, Saniel says MAZEPT1_AUTO3_SUCCESS

    # at the start of level #(tbd), Saniel says MAZEPT1_AUTO4

    # at the start of level #(tbd, the final level), Riley says MAZEPT1_AUTO5
    # then Ada says MAZEPT1_AUTO5_ADA which has _HINT1
    # when we restart this level because the user lost, Riley says MAZEPT1_AUTO5_FAILURE
    # then Ada says MAZEPT1_AUTO5_FAILURE_ADA
    # then Faber says MAZEPT1_AUTO5_SUCCESS
    # When we start MAZEPT2 we will start Riley Maze app from this same level.

    def step_success(self):
        self.wait_confirm('SUCCESS')
        # wait for the user to click the button
        self.complete = True
        # bools that define quest behavior, other ppl reference them
        self.available = False
        # this is almost always the opposite of complete
        Sound.play('quests/quest-complete')
        self.stop()
