# from eosclubhouse.apps import Maze
from eosclubhouse.apps import Fizzics  # just for testing
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class MazePt1(Quest):

    __available_after_completing_quests__ = ['TrapIntro']

    def __init__(self):
        super().__init__('MazePt1', 'ada')
        # self._app = Maze()
        self._app = Fizzics()
        # for testing the app, since the maze hooks aren't in yet

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH_ADA')
        self.wait_confirm('RILEYHELLO')
        self.wait_confirm('EXIT')
        return self.step_play_level

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_play_level(self):
        current_level = self._app.get_current_level()
        if current_level >= 1:  # should be == when rileymaze hooks get in
            self.show_hints_message('MANUAL1')
        # self.wait_for_app_js_props_changed(self._app, ['level'])
        self.pause(7)
        return self.step_level2
        # return self.step_success
        # and now we move on to the end of the quest step

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level2(self):
        self.wait_confirm('MANUAL2')
        return self.step_level3
        # if we ever restart a level whose #<X (see below) because the user lost, Riley plays
        # MAZEPT1_DIED_RESTART

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_level3(self):
        self.wait_confirm('MANUAL3')
        return self.step_levelx

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_levelx(self):
        self.show_hints_message('MANUAL4')
        return self.step_levely

    @Quest.with_app_launched(Fizzics.APP_NAME)
    def step_levely(self):
        self.wait_confirm('AUTO1_FELIX')
        self.wait_confirm('AUTO1_FABER')
        self.wait_confirm('AUTO1_ADA')
        self.wait_confirm('AUTO1_RILEY')
        self.wait_confirm('AUTO1_SANIEL')
        self.show_hints_message('AUTO1')
        self.pause(7)
        self.show_hints_message('AUTO2')
        self.pause(7)
        self.show_hints_message('AUTO3')
        self.wait_confirm('AUTO4_BACKSTORY')
        self.wait_confirm('AUTO4_BACKSTORY2')
        self.wait_confirm('AUTO5')
        self.show_hints_message('AUTO5_ADA')
        self.pause(7)
        return self.step_success

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
