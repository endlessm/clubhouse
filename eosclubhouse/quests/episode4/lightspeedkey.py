from eosclubhouse.libquest import Quest
from eosclubhouse.system import Sound, ToolBoxTopic
from eosclubhouse.apps import LightSpeed


class LightspeedKey(Quest):

    __available_after_completing_quests__ = ['MazePt1']

    FIRST_LEVEL = 15
    LAST_LEVEL = 17

    # Maps the toolbox panels to the labels used in message IDs:
    MESSAGES_FOR_PANELS = {
        'game': 'GAME',
        'spawn': 'SPAWN',
        'updateAsteroid': 'ASTEROID',
        'updateSpinner': 'SPINNER',
        'updateSquid': 'SQUID',
        'updateBeam': 'BEAM',
        'activatePowerup': 'POWERUPS',
    }

    def __init__(self):
        super().__init__('LightspeedKey', 'faber')
        self._app = LightSpeed()

    def step_begin(self):
        self.ask_for_app_launch(self._app, pause_after_launch=2)
        self._toolbox_topics = {}
        return self.step_setup

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_setup(self):
        for topic_name in ['game', 'spawn', 'updateAsteroid', 'updateSpinner',
                           'updateSquid', 'updateBeam', 'activatePowerup']:
            self._app.reveal_topic(topic_name)
            toolbox_topic = ToolBoxTopic(self._app.APP_NAME, topic_name)
            self._toolbox_topics[topic_name] = toolbox_topic

        self._app.set_js_property('availableLevels', ('i', self.LAST_LEVEL))
        self._app.set_level(self.FIRST_LEVEL)
        return self.step_abouttoplay

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_abouttoplay(self):
        if not self._app.get_js_property('playing'):
            self.wait_for_app_js_props_changed(self._app, ['playing', 'flipped'])

        if self._app.get_js_property('flipped'):
            return self.step_incode

        current_level = self._app.get_js_property('currentLevel', 0)
        if current_level > self.LAST_LEVEL:
            return self.step_success
        elif current_level < self.FIRST_LEVEL:
            return self.step_setup

        message_id = "LEVELS{}".format(int(current_level - self.FIRST_LEVEL + 1))
        self.show_hints_message(message_id)

        return self.step_inlevel, current_level

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_inlevel(self, current_level):
        self.wait_for_app_js_props_changed(self._app, ['flipped', 'playing', 'success'])

        if self._app.get_js_property('flipped'):
            return self.step_incode

        if self._app.get_js_property('success') and current_level == self.LAST_LEVEL:
            return self.step_success

        if not self._app.get_js_property('playing'):
            return self.step_abouttoplay

        return self.step_inlevel, current_level

    @Quest.with_app_launched(LightSpeed.APP_NAME)
    def step_incode(self):
        self._toolbox_topics['spawn'].set_sensitive(False)

        clicked_actions = []
        for toolbox_topic in self._toolbox_topics.values():
            clicked_action = self.connect_toolbox_topic_clicked(toolbox_topic)
            clicked_actions.append(clicked_action)

        app_changes_action = self.connect_app_js_props_changes(self._app, ['flipped'])
        self.wait_for_one([*clicked_actions, app_changes_action])

        if not self._app.get_js_property('flipped'):
            return self.step_abouttoplay

        topic_clicked = self._toolbox_topic_clicked['topic']

        suffix = None
        if not self._toolbox_topics[topic_clicked].get_sensitive():
            suffix = 'LOCKED'
        else:
            suffix = self.MESSAGES_FOR_PANELS[topic_clicked]
        self.show_hints_message('PANEL_' + suffix)

        return self.step_incode

    def step_success(self):
        self.wait_confirm('SUCCESS')
        self.give_item('item.key.sidetrack.1')
        self.complete = True
        self.available = False
        Sound.play('quests/quest-complete')
        self.stop()
