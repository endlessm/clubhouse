from eosclubhouse.apps import Maze  # this is the code in apps.py that defines hooks into the maze app 
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class MazePt1(Quest):


	# initalize basic quest stuff
    def __init__(self):
        super().__init__('MazePt1', 'riley')  # super() calls the __init__() which is a python constructor in the parent class .  MazePt1 is the class we are defining rn.   riley is the current character defined 
        self._app = Maze()   # self is the same as C#'s keyword this,  and _ before a var name is because internal only (not usually exposed outside the class), and Maze() calls the constructor of the Maze class, ie - it instantiates it so from now when we refer to _app, we can communciate with the Maze app via the Maze class

    def step_begin(self):
	# by default this function already uses _QUESTION and _ACCEPT and _ABORT
	# quest starts by clicking on Riley in the clubhouse
	# Riley asks:  MAZEPT1_QUESTION
	# user can reply:  MAZEPT1_QUESTION_ACCEPT  or _ABORT


	# if user does _ACCEPT, then Riley replies with _TRANSFER
        self.wait_confirm('TRANSFER')   # self.wait_confirm(dialog string) = display this dialog and wait for the user to click on it
	# note that the MAZEPT1_ part is always automatically pre-pended, so you don't include it 

	# this following stuff will require changing game state variables
	# 	and simultaneously during this dialog:
	#	Riley art disappears inside Clubhouse
	#	RileyMaze app installed on user's desktop


	# this next part goes in each character's quest set file:
	# if still in the Clubhouse, if the user clicks on the 3 other characters, they get dialog encouraging them to launch the app:
	# MAZEPT1_LAUNCH_ADA
	# MAZEPT1_LAUNCH_FABER
	# MAZEPT1_LAUNCH_SANIEL

	# MORE GENERAL STUFF
	# provide mention of indentation requirements from python
	# how to define a new ep = it looks for the folder name, and you also need the __init__ file inside that folder

	# wait for the user to launch the app
	# see file /clubhouse/apps.py - and there is a class for each app and it defines hooks where that app can communciate with quest - for example, which variables you need to reference for quest logic, such as current level or whether the user dies
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH_ADA')  # this method will present the message._id dialog, and go away once self._app has launched, and it will also highlight the icon on the desktop.  if there is LAUNCH_ADA_HINT1, then it will also use that.  the pause happens now, before we move to the next step in this script, to give the app time to ramp up.

        return step_play_level  # this moves the code along to the next step. when you return this step, the parent class runs it



    @Quest.with_app_launched(Maze.APP_NAME)  # the @ is python 'decorator' which is like a wrapper around the method we're about to define.  in this case, if the user closes the app during this step, we go to step abort()
    def step_play_level(self):    # each step is basically the node of a graph.  Manuel just said this, not sure if it's important at this level.
 
        current_level = self._app.get_current_level()  # this is how you declare a local var, you don't need to give it a type

	# when the user launches the app:
	# Riley says MAZEPT1_MANUAL1 which hasMAZEPT1_MANUAL1_HINT1 _HINT2 and _HINT3
        if current_level == 1:
                self.show_hints_message('MAZEPT1_MANUAL1');  # unfort here you must prepend the entire string id
		#  show_hints_message() differs from wait_confirm() in that it operates asynchronously, it doesn't block downstream steps if the user doesn't click on it.  also it gives the message in a loop.
		# and it automatically knows to loop through the _HINT# variations and then asks "what is my goal?" then loops back to
	

        self.wait_for_app_js_props_changed(self._app, ['level'])  # js is java script, so this refers to our App class that we use here (see above), and this is a list (which is what py calls arrays) of the properties (which are basically java script variables) which we are waiting for them to change.  for now, it's just level, but it could be user dying or similar.

        return self.step_success


    def step_success(self):
        self.wait_confirm('SUCCESS')
        step.complete = True   # bools that define quest behavior, other ppl reference them
        step.available = False   # is almost always the opposite of complete
        Sound.play('quests/quest-complete')
        self.stop()   # actually stops the quest code








	# if we ever restart a level whose #<X (see below) because the user lost, Riley plays
	# MAZEPT1_DIED_RESTART


	# at the start of level 2, Riley says MAZEPT1_MANUAL2


	# at the start of level 3, Saniel says MAZEPT1_MANUAL3


	# at the start of level #(tbd), Saniel says MAZEPT1_MANUAL4 which has _HINT1


	# at the start of level #(tbd), Riley says MAZEPT1_AUTO1
	# then Felix says MAZEPT1_AUTO1_FELIX
	# then Faber says MAZEPT1_AUTO1_FABER
	# then Ada says MAZEPT1_AUTO1_ADA
	# then Riley says MAZEPT1_AUTO1_RILEY
	# then Saniel says MAZEPT1_AUTO1_SANIEL which has _HINT1


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

	



# below here = old code from another quest in a prior episode


#    def __init__(self):
#        super().__init__('SetUp', 'riley')

#    def step_begin(self):
#        self.wait_confirm('EXPLAIN')
#        self.wait_confirm('EXPLAIN2')
#        return self.step_success

#    def step_success(self):
#        self.wait_confirm('END')
#        self.complete = True
#        self.available = False
#        Sound.play('quests/quest-complete')
#        self.stop()
