from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound
from eosclubhouse.apps import Sidetrack
# from eosclubhouse import logger


class BonusRound(Quest):

    __available_after_completing_quests__ = ['MazePt4']

    def __init__(self):
        super().__init__('BonusRound', 'riley')
        self._app = Sidetrack()

    def is_unlocked(self):
        lock_state = self.gss.get('lock.sidetrack.3')
        return lock_state is not None and not lock_state.get('locked', True)

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        self._app.set_js_property('availableLevels', ('u', 50))
        return self.step_inlevel

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_inlevel(self):
        current_level = int(self._app.get_js_property('currentLevel'))
        if current_level == 41:
            self.wait_confirm('LEVELS1')
            self.show_hints_message('LEVELS1_B')
        elif current_level == 42:
            self.wait_confirm('LEVELS2')
            self.show_hints_message('LEVELS2_B')
        elif current_level > 42 and current_level < 46:
            msg_id = 'LEVELS' + str(current_level - 40)
            self.show_hints_message(msg_id)
        elif current_level == 46:
            self.wait_confirm('LEVELS6')
            self.show_hints_message('LEVELS6_B')
        elif current_level == 47:
            self.wait_confirm('LEVELS7')
            # give the Sidetrack level editing key
            if not self.is_unlocked():
                self.give_item('item.key.sidetrack.3')
            self.wait_confirm('LEVELS7_B')
            self.wait_confirm('LEVELS7_FLIP')
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
            return self.step_level47_lock
        elif current_level == 48:
            self.show_hints_message('LEVELS8')
        elif current_level == 49:
            self.show_hints_message('LEVELS9')
        elif current_level == 50:
            self.show_hints_message('LEVELS10')
            self.show_hints_message('LEVELS10_B')
            self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
            return self.step_success
        self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
        return self.step_inlevel

    @Quest.with_app_launched(Sidetrack.APP_NAME)
    def step_level47_lock(self):
        # have to split this out so it can loop
        if not self.is_unlocked():
            self.pause(1)
            return self.step_level47_lock
        self.wait_confirm('LEVELS7_LEVELCODE1')
        self.wait_confirm('LEVELS7_LEVELCODE2')
        self.show_hints_message('LEVELS7_LEVELCODE3')
        self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
        return self.step_inlevel

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
