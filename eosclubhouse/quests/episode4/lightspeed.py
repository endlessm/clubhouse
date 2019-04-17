from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class Lightspeed(Quest):

    __available_after_completing_quests__ = ['MazePt1']
    # Dummy code to stub in quest
    def __init__(self):
        super().__init__('Lightspeed', 'faber')

    def step_begin(self):
        self.wait_confirm('LEVELS1')
        self.wait_confirm('LEVELS2')
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()

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
