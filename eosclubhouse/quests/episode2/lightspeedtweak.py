from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedTweak(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'
    LEVEL_ID = 2

    def __init__(self):
        super().__init__('LightSpeed Tweak', 'ada')
        self._app = LightSpeed()
        self._step_to_continue = None

    def get_current_score(self):
        if self.debug_skip():
            self._level += 1
        else:
            self._level = self._app.get_js_property('score', 0)
        return self._level

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)

        self._app.set_level(self.LEVEL_ID)
        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        self.show_hints_message('EXPLANATION')
        if not self._app.get_js_property('playing'):
            self.wait_for_app_js_props_changed(self._app, ['playing'])
        return self.step_playing

    @Quest.with_app_launched(APP_NAME)
    def step_wrong_level(self):
        self.show_hints_message('WRONGLEVEL')
        if self._app.get_js_property('currentLevel') == self.LEVEL_ID:
            return self._step_to_continue
        self.wait_for_app_js_props_changed(self._app, ['currentLevel'])
        return self.step_wrong_level

    @Quest.with_app_launched(APP_NAME)
    def step_playing(self):
        if self._app.get_js_property('playing'):
            self.wait_for_app_js_props_changed(self._app, ['playing', 'currentLevel'], timeout=10)
        if self._app.get_js_property('currentLevel') != self.LEVEL_ID:
            self._step_to_continue = self.step_explanation
            return self.step_wrong_level

        return self.step_fliptohack

    @Quest.with_app_launched(APP_NAME)
    def step_fliptohack(self):
        if self._app.get_js_property('flipped'):
            return self.step_unlock

        self.show_hints_message('FLIPTOHACK')

        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_fliptohack

    def _is_panel_unlocked(self):
        item = self.gss.get('item.key.lightspeed.1')
        return item is not None and item.get('used', False)

    @Quest.with_app_launched(APP_NAME)
    def step_unlock(self):
        if self._is_panel_unlocked():
            return self.step_hack

        self.show_hints_message('UNLOCK')

        while not (self._is_panel_unlocked() or self.debug_skip()) and not self.is_cancelled():
            self.connect_gss_changes().wait()

        return self.step_hack

    @Quest.with_app_launched(APP_NAME)
    def step_hack(self):
        self.show_hints_message('HACK')
        if self._app.get_js_property('flipped'):
            self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_abouttoplay

    @Quest.with_app_launched(APP_NAME)
    def step_abouttoplay(self):
        if not self._app.get_js_property('playing'):
            self.show_hints_message('ABOUTTOPLAY')
            self.wait_for_app_js_props_changed(self._app, ['playing'])
        return self.step_playtest

    @Quest.with_app_launched(APP_NAME)
    def step_playtest(self):
        self.show_hints_message('PLAYTEST')

        if not self._app.get_js_property('success') and not self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['success', 'currentLevel'])

        if self._app.get_js_property('success'):
            self.show_confirm_message('SUCCESS').wait()
            return self.step_end

        if self._app.get_js_property('currentLevel') != self.LEVEL_ID:
            self._step_to_continue = self.step_playtest
            return self.step_wrong_level

        return self.step_playtest

    def step_end(self):
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()
        self.stop()
