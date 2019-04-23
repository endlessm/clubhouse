from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
# from eosclubhouse.apps import Maze
from eosclubhouse.apps import Fizzics


class MazePt2(Quest):

    __available_after_completing_quests__ = ['Lightspeed']

    def __init__(self):
        super().__init__('MazePt2', 'ada')
        self._app = Fizzics()
        # self._app = Maze()

    def step_begin(self):
        # quest starts by clicking on Ada in the clubhouse
        # Ada asks:  MAZEPT2_QUESTION
        # user can reply:  MAZEPT2_QUESTION_ACCEPT  or _ABORT
        # if user does _ACCEPT, then if Riley Maze is not currently launched,
        # Ada replies with MAZEP2_LAUNCH which has _HINT1 until the user launches Riley Maze
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        return self.step_app_launched

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_app_launched(self):
        self.show_hints_message('FLIP')
        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        self.show_hints_message('INSTRUCTIONS')
        self.pause(15)
        self.show_hints_message('LEVELS2')
        self.pause(15)
        self.show_hints_message('LEVELS3')
        self.pause(15)
        self.wait_confirm('LEVELS4_ADA1')
        self.wait_confirm('LEVELS4_FABER1')
        self.wait_confirm('LEVELS4_ADA2')
        self.wait_confirm('LEVELS4_FABER2')
        self.wait_confirm('LEVELS4_ADA3')
        self.wait_confirm('LEVELS5')
        self.wait_confirm('LEVELS5_RILEY')
        self.wait_confirm('RESEARCH1')
        self.wait_confirm('RESEARCH2')
        self.wait_confirm('LEVELS6')
        # felix line
        # self.wait_confirm('LEVELS6_FELIX')
        self.wait_confirm('LEVELS6_FABER')
        self.wait_confirm('LEVELS6_RILEY')
        self.wait_confirm('LEVELS6_ADA')
        # felix line
        # self.wait_confirm('IMPASSABLE')
        self.wait_confirm('IMPASSABLE_FABER')
        self.wait_confirm('IMPASSABLE_RILEY')
        # inside Riley Maze app, at the start of level 1, if the app is not flipped,
        # Ada says MAZEPT2_FLIP which has _HINT1 until the app is flipped
        # this will present the user with a locked panel
        # and they can click on it to unlock it with the key they must have
        # (since this quest only unlocks when the user acquires that key)
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
        # then Ada says MAZEPT2_SUCCESS which is the end of this quest.
        # The user does not (and, in fact, cannot) beat the current level,
        # and when they return to this app for MAZEPT3 they will return to this same level
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
