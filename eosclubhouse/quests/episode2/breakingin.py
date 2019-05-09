from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class BreakingIn(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'
    LEVEL2_LOCK = 'lock.OperatingSystemApp.2'

    __available_after_completing_quests__ = ['MakeDevice']
    __complete_episode__ = True
    __advance_episode__ = True

    def __init__(self):
        super().__init__('BreakingIn', 'riley')
        self._app = App(self.APP_NAME)

        # Make sure the quest is doable, if it was left incomplete but with Riley trapped (early
        # aborted).
        self._ensure_is_unblocked()

    def _ensure_is_unblocked(self):
        if not self.complete and self.gss.get('clubhouse.character.Riley', {}).get('in_trap'):
            self.gss.set('clubhouse.character.Riley', {'in_trap': False})

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        self.show_hints_message('EXPLAIN')

        if not self._app.get_js_property('flipped') or self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['flipped'])

        return self.step_flipped

    def level2_lock_tried(self):
        if self.debug_skip():
            return True

        lock = self.gss.get(self.LEVEL2_LOCK)
        return lock is not None and lock.get('tried', False)

    def set_trap_sequence(self, sequence):
        lock = self.gss.get(self.LEVEL2_LOCK) or {}
        lock.update({'trap_sequence': sequence})
        self.gss.set(self.LEVEL2_LOCK, lock)

    def end_trap_sequence(self):
        lock = self.gss.get(self.LEVEL2_LOCK) or {}
        lock.pop('trap_sequence', None)
        lock.update({'locked': False})
        self.gss.set(self.LEVEL2_LOCK, lock)

    @Quest.with_app_launched(APP_NAME)
    def step_flipped(self):
        self.show_hints_message('FLIPPED')

        while not (self.level2_lock_tried() or self.is_cancelled()):
            self.connect_gss_changes().wait()

        return self.step_unlocked

    @Quest.with_app_launched(APP_NAME)
    def step_unlocked(self):
        self.set_trap_sequence(0)
        self.wait_confirm('UNLOCKED')
        return self.step_starttrap

    # Not aborting quest even if app exits
    def step_starttrap(self):
        self.set_trap_sequence(1)
        self.wait_confirm('STARTTRAP')
        return self.step_trapped

    def step_trapped(self):
        self.set_trap_sequence(2)
        self.wait_confirm('TRAPPED')
        self.gss.set('clubhouse.character.Riley', {'in_trap': True})
        return self.step_archivist

    def step_archivist(self):
        self.show_confirm_message('ARCHIVIST', confirm_label='End of Episode 2').wait()
        self.end_trap_sequence()
        if not self.confirmed_step():
            return

        Sound.play('quests/quest-complete')
        self.complete = True
        self.available = False
        self.stop()

    # Override the default finish
    def run_finished(self):
        super().run_finished()

        # Make sure we don't leave the quest in a state there the quest is not finished but Riley
        # is no longer available because of being in the trap.
        self._ensure_is_unblocked()
