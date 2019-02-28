from eosclubhouse.libquest import Quest
from eosclubhouse.system import App, Sound


class Investigation(Quest):

    APP_NAME = 'com.endlessm.OperatingSystemApp'
    LEVEL2_LOCK = 'lock.OperatingSystemApp.2'

    def __init__(self):
        super().__init__('Investigation', 'riley')
        self._app = App(self.APP_NAME)
        self._try_attempts = 0
        self.available = False
        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("Chore"):
            self.available = True

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        return self.step_wait_for_flip

    @Quest.with_app_launched(APP_NAME)
    def step_wait_for_flip(self, again=False):
        if self._app.get_js_property('flipped') or self.debug_skip():
            return self.step_unlock

        # FIXME display a different message if again == True
        self.show_hints_message('FLIP')
        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_wait_for_flip

    def level2_lock_tried(self):
        lock = self.gss.get(self.LEVEL2_LOCK)
        return lock is not None and lock.get('tried', False)

    @Quest.with_app_launched(APP_NAME)
    def step_unlock(self, display_message=True):
        if display_message:
            if self._try_attempts == 0:
                self.show_hints_message('UNLOCK')
            elif self._try_attempts == 1:
                self.show_hints_message('STOP')
            elif self._try_attempts >= 1:
                self.show_hints_message('STOPAGAIN')

        gsschanges_action = self.connect_gss_changes()
        flipped_action = self.connect_app_js_props_changes(self._app, ['flipped'])
        self.wait_for_one([gsschanges_action, flipped_action])

        if not self._app.get_js_property('flipped'):
            if self._try_attempts > 0:
                return self.step_end
            return self.step_wait_for_flip, True

        if self.level2_lock_tried():
            self._try_attempts += 1
            return self.step_unlock

        # Don't display message if the game state changed for any
        # other reason.
        return self.step_unlock, False

    def step_end(self):
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()

        self.stop()
