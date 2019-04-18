from eosclubhouse.apps import Maze  # this is the code in apps.py that defines hooks into the maze app 
from eosclubhouse.apps import Fizzics # just for testing
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound

class MazePt1(Quest):
    # initalize basic quest stuff
    def __init__(self):
        super().__init__('MazePt1', 'riley')
        # super() calls __init__() which is a python constructor in the parent class
        # MazePt1 is the class we are defining rn, and riley is the current character
        ###self._app = Maze()
        # self is the same as C#'s keyword this
        # using _ (underscore) before a var name is the convention when it's a class internal variable.
        # Maze() calls the constructor of the Maze class, so now _app refers to that instance of Maze.
        # This allows us to call hooks from that app (which are defined in ../apps.py)
        self._app = Fizzics()
        # for testing the app, since the maze hooks aren't in yet

    def step_begin(self):
    # by default this function already uses _QUESTION and _ACCEPT and _ABORT
    # quest starts by clicking on Riley in the clubhouse
    # Riley asks:  MAZEPT1_QUESTION
    # user can reply:  MAZEPT1_QUESTION_ACCEPT  or _ABORT
    # if user does _ACCEPT, then Riley replies with _TRANSFER
        self.wait_confirm('TRANSFER')
        # self.wait_confirm(dialog string) = display this dialog and wait for the user to click on it
        # note that the MAZEPT1_ part is always automatically pre-pended, so you don't include it 
        # this following stuff will require changing game state variables
        #   simultaneously during this dialog:
        #   Riley art disappears inside Clubhouse
        #   RileyMaze app installed on user's desktop
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH_ADA')
        # wait for the user to launch the app
        # this method will present the message._id dialog, and go away 
        # once self._app has launched, and it will also highlight the icon on the desktop.
        # if there is LAUNCH_ADA_HINT1, then it will also use that. 
        # the pause happens now, before we move to the next step in this script, to give the app time to ramp up.
        return self.step_play_level 
        # here, we return a function (defined below), which will be run by the parent class.
        # Thsi is how we move to the next step of the quest.

    @Quest.with_app_launched(Fizzics.APP_NAME) # was calling the class directly but why not this?
    def step_play_level(self):    
    # the @ is shorthand notation for a 'decorator'. Decorators are functions that take a function as their argument.
    # in this case, the decorator lets us detect if the user closes the app during this step, so we can go to step abort()
    # each step is basically the node of a graph.  Manuel just said this, not sure if it's important at this level.
        current_level = self._app.get_current_level()  # this is how you declare a local var, you don't need to give it a type
        # when the user launches the app:
        # Riley says MAZEPT1_MANUAL1 which has MAZEPT1_MANUAL1_HINT1 _HINT2 and _HINT3
        if current_level >= 1: #should be == when rileymaze hooks get in
            self.show_hints_message('MAZEPT1_MANUAL1');  # Here you must prepend the entire string id
            # show_hints_message() differs from wait_confirm() in that it operates asynchronously
            # it doesn't block downstream steps if the user doesn't click on it.
            # also, it loops through a set of messages: the _HINT# variations,
            # and then asks "what is my goal?" before restarting
        
        ###self.wait_for_app_js_props_changed(self._app, ['level'])
        # js means javascript, so this refers to the App class we defined at the beginning.
        # this is a list (which is what py calls arrays) of the properties (which are basically java script variables)
        # which we are waiting for the player to change before we move to the next step.
        # for now, it's just level, but it could be user dying or similar.
        self.pause(10)
        return self.step_success
        # and now we move on to the end of the quest step

    def step_level2(self):
        # at the start of level 2, Riley says MAZEPT1_MANUAL2
        return 0
    # if we ever restart a level whose #<X (see below) because the user lost, Riley plays
    # MAZEPT1_DIED_RESTART

    def step_level3(self):
        # at the start of level 3, Saniel says MAZEPT1_MANUAL3
        return 0

    def step_levelx(self):
       # at the start of level #(tbd), Saniel says MAZEPT1_MANUAL4 which has _HINT1
       return 0
       
    def step_levely(self):
       # at the start of level #(tbd), Riley says MAZEPT1_AUTO1
       # then Felix says MAZEPT1_AUTO1_FELIX
       # then Faber says MAZEPT1_AUTO1_FABER
       # then Ada says MAZEPT1_AUTO1_ADA
       # then Riley says MAZEPT1_AUTO1_RILEY
       # then Saniel says MAZEPT1_AUTO1_SANIEL which has _HINT1
       return 0

    # at the start of level X(tbd), Saniel says MAZEPT1_AUTO2 which has _HINT1
    
    # at the start of level X+1, Saniel says MAZEPT1_AUTO3 which has _HINT1 and _HINT2
    # if we restart this level because the user lost, Saniel says MAZEPT1_AUTO3_FAILURE 
    # if the player finishes this level successfully, Saniel says MAZEPT1_AUTO3_SUCCESS

    # at the start of level #(tbd), Saniel says MAZEPT1_AUTO4

    # at the start of level #(tbd, the final level), Riley says MAZEPT1_AUTO5
    # then Ada says MAZEPT1_AUTO5_ADA which has _HINT1
    # when we restart this level because the user lost (which necessarily happens), Riley says MAZEPT1_AUTO5_FAILURE
    # then Ada says MAZEPT1_AUTO5_FAILURE_ADA
    # then Faber says MAZEPT1_AUTO5_SUCCESS
    # that's the final dialog of this quest.  The Quest is over, even though we didn't complete this level.  When we start MAZEPT2 we will start Riley Maze app from this same level.

    def step_success(self):
        self.wait_confirm('SUCCESS')
        # wait for the user to click the button
        self.complete = True
        # bools that define quest behavior, other ppl reference them
        self.available = False
        # this is almost always the opposite of complete
        Sound.play('quests/quest-complete')
        self.stop()
        # actually stops the quest code