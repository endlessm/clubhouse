from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack
from eosclubhouse import logger


class MazePt1(Quest):

    __available_after_completing_quests__ = ['TrapIntro']

    def __init__(self):
        super().__init__('MazePt1', 'ada')
        self._app = Sidetrack()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH_ADA')
        self._app.set_js_property('availableLevels', ('u', 23))
        logger.debug('available levels = %i', int(self._app.get_js_property('currentLevel')))
        self.wait_confirm('RILEYHELLO')
        self.wait_confirm('EXIT')
        return self.step_play_level

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self):
        current_level = int(self._app.get_js_property('currentLevel'))
        if current_level == 1:
            self.show_hints_message('MANUAL1')
            self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'success'])
            if not self._app.get_js_property('success'):
                logger.debug("player died")
                self.wait_confirm('DIED_RESTART')
            return self.step_play_level
        elif current_level == 2:
            self.wait_confirm('MANUAL2')
        elif current_level == 3:
            self.wait_confirm('MANUAL3')
        elif current_level == 4:
            self.show_hints_message('MANUAL4')
        elif current_level == 6:
            self.show_hints_message('MANUAL5')
        elif current_level == 7:
            self.wait_confirm('ROBOTS1')
            self.wait_confirm('ROBOTS2')
            self.show_hints_message('ROBOTS3')
        elif current_level == 10:
            self.wait_confirm('MOREROBOTS')
        elif current_level == 14:
            self.wait_confirm('AUTO1')
            # felix destroys the controls here
            self._app.set_js_property('controlsCutscene', ('b', True))
            logger.debug("started cutscene")
            self.pause(1)
            self.wait_for_app_js_props_changed(self._app, ['controlsCutscene'])
            logger.debug("detected cutscene state change")
            self.wait_confirm('AUTO1_FELIX')
            self.wait_confirm('AUTO1_FABER')
            self.wait_confirm('AUTO1_ADA')
            self.wait_confirm('AUTO1_RILEY')
            self.show_hints_message('AUTO1_SANIEL')
        elif current_level == 15:
            self.show_hints_message('AUTO2')
        elif current_level == 16:
            self.show_hints_message('AUTO3')
            self.wait_for_app_js_props_changed(self._app, ['currentLevel', 'success'])
            if not self._app.get_js_property('success'):
                logger.debug("player died")
                self.wait_confirm('AUTO3_FAILURE')
                return self.step_play_level
            else:
                self.wait_confirm('AUTO3_SUCCESS')
                # pause so user can see dialogue
                self.pause(5)
                return self.step_play_level
        elif current_level == 17:
            self.wait_confirm('AUTO4_BACKSTORY')
            self.wait_confirm('AUTO4_BACKSTORY2')
            self.wait_confirm('AUTO4_BACKSTORY3')
            self.wait_confirm('AUTO4_BACKSTORY4')
            self.wait_confirm('AUTO4_BACKSTORY5')
            self.wait_confirm('AUTO4_BACKSTORY6')
            self.wait_confirm('AUTO4_BACKSTORY7')
            self.wait_confirm('AUTO4_BACKSTORY8')
            self.wait_confirm('AUTO4_BACKSTORY9')
            self.wait_confirm('AUTO4_BACKSTORY10')
        elif current_level == 18:
            self.wait_confirm('ONEJUMP')
            self.show_hints_message('ONEJUMP_ADA')
        elif current_level == 19:
            self.wait_confirm('ONEFORWARD')
            self.show_hints_message('ONEFORWARD_ADA')
        elif current_level == 20:
            self.wait_confirm('SLIDING')
        elif current_level == 21:
            self.wait_confirm('WASTEJUMPS')
        elif current_level == 22:
            self.wait_confirm('DRAMA_ADA1')
            self.wait_confirm('DRAMA_FABER1')
            self.wait_confirm('DRAMA_ADA2')
            self.wait_confirm('DRAMA_FABER2')
            self.wait_confirm('DRAMA_ADA3')
        elif current_level == 23:
            self.wait_confirm('AUTO5')
            self.show_hints_message('AUTO5_ADA')
            # wait for the player to die, as they cannot pass this level
            self.wait_for_app_js_props_changed(self._app, ['success'])
            self.wait_confirm('AUTO5_FAILURE_ADA')
            self.wait_confirm('AUTO5_FAILURE_ADA2')
            return self.step_success
        self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
        return self.step_play_level

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
