from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Lightspeed(Quest):


	# initalize basic quest stuff


	# quest starts by clicking on Faber in the clubhouse
	# Faber asks:  LIGHTSPEED_QUESTION
	# user can reply:  LIGHTSPEED_QUESTION_ACCEPT  or _ABORT
	# if user does _ACCEPT, then Faber says LIGHTSPEED_LAUNCH which has _HINT1


	# there are 5 levels to the Lightspeed quest.  for each level #:
	# at the beginning of the level, Faber says LIGHTSPEED_LEVELS# which has _HINT1


	# if the user beats level 5, Faber says LIGHTSPEED_SUCCESS and gives the player the key: Riley Maze Instructions Panel


	# if the user flips the app and clicks on a coding panel, Faber responds as follows:
	# LIGHTSPEED_PANEL_LOCKED - if the panel they've clicked on is not available this level
	# LIGHTSPEED_PANEL_GAME- if they click on the Game panel
	# LIGHTSPEED_PANEL_SPAWN - if they click on the Spawn panel
	# LIGHTSPEED_PANEL_ASTEROID - if they click on the Asteroid panel
	# LIGHTSPEED_PANEL_SPINNER - if they click on the Spinner panel
	# LIGHTSPEED_PANEL_SQUID - if they click on the Squid panel
	# LIGHTSPEED_PANEL_BEAM - if they click on the Beam panel
	# LIGHTSPEED_PANEL_POWERUPS - if they click on the PowerUps panel
	



	

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
