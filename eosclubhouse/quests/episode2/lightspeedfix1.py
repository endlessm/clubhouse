from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedFix1(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    __available_after_completing_quests__ = ['LightSpeedTweak']

    def __init__(self):
        super().__init__('LightSpeedFix1', 'saniel')
        self._app = LightSpeed()

    def step_begin(self):
        if not self._app.is_running():
            self.show_hints_message('LAUNCH')
            self.give_app_icon(self.APP_NAME)

            self.wait_for_app_launch(self._app, pause_after_launch=2)

        return self.step_explanation

    @Quest.with_app_launched(APP_NAME)
    def step_explanation(self):
        self.show_hints_message('EXPLANATION')

        # @todo: Alert the user something was wrong is the level couldn't be set
        self._app.set_level(3)

        if not self._app.get_js_property('playing'):
            self.wait_for_app_js_props_changed(self._app, ['playing'])
        return self.step_playing

    @Quest.with_app_launched(APP_NAME)
    def step_playing(self):
        if self._app.get_js_property('playing'):
            self.wait_for_app_js_props_changed(self._app, ['playing'], timeout=10)

        return self.step_fliptohack

    @Quest.with_app_launched(APP_NAME)
    def step_fliptohack(self):
        if self._app.get_js_property('flipped'):
            return self.step_unlock

        self.show_hints_message('EXPLANATION2')

        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_fliptohack

    def _is_panel_unlocked(self):
        item = self.gss.get('lock.lightspeed.2')
        return item is not None and not item.get('locked', True)

    @Quest.with_app_launched(APP_NAME)
    def step_unlock(self):
        self.show_hints_message('UNLOCK')

        while not (self._is_panel_unlocked() or self.debug_skip()) and not self.is_cancelled():
            self.connect_gss_changes().wait()

        return self.step_code

    @Quest.with_app_launched(APP_NAME)
    def step_code(self):
        if self._app.get_js_property('success') or self.debug_skip():
            return self.step_success

        self._app.reveal_topic('spawnEnemy')

        self.show_hints_message('CODE')
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
        self.wait_for_app_js_props_changed(self._app, ['success'])
        return self.step_code

    def step_success(self):
        self.complete = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()

        self.stop()
