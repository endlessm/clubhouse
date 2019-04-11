from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class MazePt1(Quest):


	# initalize basic quest stuff


	# quest starts by clicking on Ada in the clubhouse
	# Ada asks:  MAZEPT2_QUESTION
	# user can reply:  MAZEPT2_QUESTION_ACCEPT  or _ABORT
	# if user does _ACCEPT, then if Riley Maze is not currently launched, Ada replies with MAZEP2_LAUNCH which has _HINT1 until the user launches Riley Maze


	# inside Riley Maze app, at the start of level 1, if the app is not flipped, Ada says MAZEPT2_FLIP which has _HINT1 until the app is flipped
	# this will present the user with a locked panel and they can click on it to unlock it with the key they necessarily have (since this quest only unlocks when the user acquires that key)
	# there is not currently any hint dialog to prompt the user to use their key on the locked panel
	# once the panel is unlocked, Ada says MAZEPT2_INSTRUCTIONS which has _HINT1 and _HINT2


	# at the start of level 2, Riley says MAZEPT2_LEVELS2 which has _HINT1 through _HINT4


	# at the start of level #(tbd), Faber says MAZEPT2_LEVELS3 which has _HINT1 through _HINT4


	# at the start of level #(tbd), Ada says MAZEPT2_LEVELS4_ADA1
	# then Faber says MAZEPT2_LEVELS4_FABER1
	# then Ada says MAZEPT2_LEVELS4_ADA2
	# then Faber says MAZEPT2_LEVELS4_FABER2
	# then Ada says MAZEPT2_LEVELS4_ADA3


	# at the start of level #(tbd), Ada says MAZEPT2_LEVELS5
	# then Riley says MAZEPT2_LEVELS5_RILEY
	# when the user finishes that level, Riley says MAZEPT2_RESEARCH1
	# then Ada says MAZEPT2_RESEARCH2


	# at the start of level #(tbd), Riley says MAZEPT2_LEVELS6
	# then Felix says MAZEPT2_LEVELS6_FELIX
	# then Faber says MAZEPT2_LEVELS6_FABER
	# then Riley says MAZEPT2_LEVELS6_RILEY
	# then Ada says MAZEPT2_LEVELS6_ADA


	# at the start of level #(tbd), Felix says MAZEPT2_IMPASSABLE
	# then Faber says MAZEPT2_IMPASSABLE_FABER
	# then Riley says MAZEPT2_IMPASSABLE_RILEY
	# then Ada says MAZEPT2_SUCCESS which is the end of this quest.  The user does not (and, in fact, cannot) beat the current level, and when they return to this app for MAZEPT3 they will return to this same level




	

# below here = old code from another quest in a prior episode


    def __init__(self):
        super().__init__('SetUp', 'riley')

    def step_begin(self):
        self.wait_confirm('EXPLAIN')
        self.wait_confirm('EXPLAIN2')
        return self.step_success

    def step_success(self):
        self.wait_confirm('END')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
