from eosclubhouse.apps import LightSpeed
from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound


class LightSpeedFix1(Quest):

    APP_NAME = 'com.endlessm.LightSpeed'

    def __init__(self):
        super().__init__('LightSpeedFix1', 'saniel')
        self._app = LightSpeed()

        self.available = False

        self.gss.connect('changed', self.update_availability)
        self.update_availability()

    def update_availability(self, gss=None):
        if self.conf['complete']:
            return
        if self.is_named_quest_complete("LightSpeedTweak"):
            self.available = True

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
            return self.step_givekey

        self.show_hints_message('EXPLANATION2')

        self.wait_for_app_js_props_changed(self._app, ['flipped'])
        return self.step_fliptohack

    @Quest.with_app_launched(APP_NAME)
    def step_givekey(self):
        lightSpeedKey = 'item.key.lightspeed.2'
        if self.gss.get(lightSpeedKey) is not None:
            return self.step_unlock

        self.wait_confirm('GIVEKEY')
        self.give_item(lightSpeedKey)
        return self.step_unlock

    def _is_panel_unlocked(self):
        item = self.gss.get('item.key.lightspeed.2')
        return item is not None and item.get('used', False)

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

        self.show_hints_message('CODE')

        self.wait_for_app_js_props_changed(self._app, ['success'])
        return self.step_code

    def step_success(self):
        self.conf['complete'] = True
        self.available = False

        Sound.play('quests/quest-complete')
        self.show_confirm_message('SUCCESS', confirm_label='Bye').wait()

        self.stop()
