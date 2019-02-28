from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedTweak(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeed Tweak', 'ada')
        self._app = LightSpeed()

    def get_current_score(self):
        if self.debug_skip():
            self._level += 1
        else:
            self._level = self._app.get_js_property('score', 0)
        return self._level

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)
            self.wait_for_app_launch(self._app, pause_after_launch=2)

        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        self.show_hints_message('EXPLANATION')
        self._app.set_level(2)

        return self.step_check_state

    @Quest.with_app_launched(APP_NAME)
    def step_check_state(self):
        if self._app.get_js_property('playing') or self.debug_skip():
            return self.step_playing

        self.wait_for_app_js_props_changed(self._app, ['playing'])
        return self.step_check_state

    @Quest.with_app_launched(APP_NAME)
    def step_playing(self):
        if self._app.get_js_property('playing'):
            self.wait_for_app_js_props_changed(self._app, ['playing'], timeout=10)

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

        if not self._app.get_js_property('success') and not self.debug_skip():
            self.wait_for_app_js_props_changed(self._app, ['success'])

        self.show_confirm_message('SUCCESS').wait()
        return self.step_givekey

    def step_givekey(self):
        key_id = 'item.key.lightspeed.2'
        if self.gss.get(key_id) is not None:
            return self.step_end
        self.show_confirm_message('GIVEITEM').wait()
        self.give_item(key_id)
        self.show_confirm_message('AFTERITEM').wait()
        return self.step_end

    def step_end(self):
        self.conf['complete'] = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.show_confirm_message('END', confirm_label='Bye').wait()
        self.stop()
