from eosclubhouse.libquest import Quest
from eosclubhouse.system import Desktop, App, Sound


class LightSpeedTweak(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeed Tweak', 'ada')
        self._app = App(self.APP_NAME)

    def get_current_score(self):
        if self.debug_skip():
            self._level += 1
        else:
            self._level = self._app.get_js_property('score', 0)
        return self._level

    def step_abort(self):
        Sound.play('quests/quest-aborted')
        self.show_message('ABORT')

        self.pause(5)
        self.stop()

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            Desktop.add_app_to_grid(self.APP_NAME)
            Desktop.focus_app(self.APP_NAME)
            self.wait_for_app_launch(self._app)

        return self.step_explanation

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_explanation(self):
        self.show_hints_message('EXPLANATION')

        levelCount = self._app.get_js_property('availableLevels')
        if levelCount < 2:
            self._app.set_js_property('availableLevels', ('i', 2))

        self._app.set_js_property('currentLevel', ('i', 1))

        return self.step_check_state

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_check_state(self):
        if self._app.get_js_property('playing') or self.debug_skip():
            return self.step_playing

        self.wait_for_app_js_props_changed(self._app, ['playing'])
        return self.step_check_state

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_playing(self):
        if self._app.get_js_property('playing'):
            self.wait_for_app_js_props_changed(self._app, ['playing'], timeout=10)

        return self.step_fliptohack

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_fliptohack(self):
        if self._app.get_js_property('flipped'):
            return self.step_givekey

        self.show_hints_message('FLIPTOHACK')

        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_fliptohack

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_givekey(self):
        self.wait_confirm('GIVEKEY')

        self.give_item('item.key.lightspeed.1')
        return self.step_unlock

    def _is_panel_unlocked(self):
        item = self.gss.get('item.key.lightspeed.1')
        return item is not None and item.get('used', False)

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_unlock(self):
        self.show_hints_message('UNLOCK')

        while not (self._is_panel_unlocked() or self.debug_skip()) and not self.is_cancelled():
            self.connect_gss_changes().wait()

        return self.step_hack

    @Quest.with_app_launched(APP_NAME, otherwise=step_abort)
    def step_hack(self):
        self.show_hints_message('HACK')

        self.wait_for_app_js_props_changed(self._app, ['success'])

        if self._app.get_js_property('success') or self.debug_skip():
            return self.step_success

        return self.step_hack

    def step_success(self):
        self.conf['complete'] = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()
        self.stop()
