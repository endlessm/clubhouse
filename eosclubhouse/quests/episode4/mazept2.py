from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack


class MazePt2(Quest):

    __available_after_completing_quests__ = ['LightspeedKey']

    def __init__(self):
        super().__init__('MazePt2', 'ada')
        self._app = Sidetrack()
        self.unlocked = False

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_wait_for_unlock(self):
        if self.is_panel_unlocked('lock.sidetrack.1'):
            self.unlocked = True
            return self.step_play_level
        else:
            self.pause(1)
            return self.step_wait_for_unlock

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2, message_id='LAUNCH')
        self._app.set_js_property('availableLevels', ('u', 28))
        highest_level = self._app.get_js_property('highestAchievedLevel')
        if 23 > highest_level > 28:
            self._app.set_js_property('highestAchievedLevel', ('u', 23))
        self._app.set_js_property('showHackdex', ('b', highest_level <= 26))
        if self.is_panel_unlocked('lock.sidetrack.1'):
            self.unlocked = True
        return self.step_play_level

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_play_level(self):
        current_level = int(self._app.get_js_property('currentLevel'))
        if current_level == 23:
            if not self.unlocked:
                self.show_hints_message('FLIP')
                return self.step_wait_for_unlock
            else:
                self.pause(4)
                self.show_hints_message('INSTRUCTIONS')
        elif current_level == 24:
            self.wait_confirm('LEVELS2')
        elif current_level == 25:
            # this text needs to be reworked at some point
            self.wait_confirm('FIXANDREORDER')
            self.pause(7)
            self.wait_confirm('FIXANDREORDER_FIXED')
        elif current_level == 26:
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            if self._app.get_js_property('success'):
                self._app.set_js_property('showHackdex', ('b', False))
                self.wait_confirm('RESEARCH1')
                self.wait_confirm('RESEARCH2')
            return self.step_play_level

        elif current_level == 28:
            for message_id in ['IMPASSABLE', 'IMPASSABLE_FABER', 'IMPASSABLE_RILEY']:
                self.wait_confirm(message_id)
            return self.step_success
        self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
        return self.step_play_level

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
