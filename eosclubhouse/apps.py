from enum import Enum
from eosclubhouse import logger
from eosclubhouse.system import App, GameStateService, ToolBoxTopic
from gi.repository import Gio, GLib


class Sidetrack(App):

    APP_NAME = 'com.endlessm.Sidetrack'

    def __init__(self):
        super().__init__(self.APP_NAME)


class Fizzics(App):

    APP_NAME = 'com.endlessm.Fizzics'
    _TOOLS = ['fling', 'move', 'create', 'delete']
    _TOOL_DISABLED_SUFFIX = 'ToolDisabled'
    _TOOL_ACTIVE_SUFFIX = 'ToolActive'
    _DISABLE_ADD_FOR_BALL_TEMPLATE = 'createType{}Disabled'
    _BALL_PROPERTIES = ['collision', 'friction', 'gravity', 'radius', 'usePhysics']
    _MULTIBALL_PROPERTIES = ['socialForce']

    class BallType(Enum):
        PLAYER = 0
        GOAL = 1
        ENEMY = 2
        ROCK = 3
        DIAMOND = 4

    def __init__(self):
        """Clubhouse App that represents the Fizzics app.

        Extra properties to connect to in this class:
          effectiveLevel -- notifies when the level is changed or beaten;
        """
        super().__init__(self.APP_NAME)

        # This is the level that the app was at, the last time we checked; it's used only for
        # skipping steps when needed.
        self._current_level = 0

        # This is the level where we consider the user to be at, i.e. usually it's the current
        # level, but we bump it if the user has also just beaten the level.
        self._effective_level = 0

    def get_effective_level(self, debug_skip=False):
        level = self.get_current_level(debug_skip)
        if self.get_js_property('levelSuccess', False):
            level += 1

        self._effective_level = level
        return level

    def get_current_level(self, debug_skip=False):
        if debug_skip:
            self._current_level += 1
            return self._current_level

        # The level obtained is zero-based, but this is too confusing
        # because the dialogues are 1-based. So we convert to
        # 1-based here:
        level = self.get_js_property('currentLevel', 0) + 1

        self._current_level = level
        return level

    def set_current_level(self, level, debug_skip=False):
        # Convert to 0-based index:
        level -= 1

        if debug_skip:
            self._current_level = level
            return

        self.set_js_property('preset', ('i', level))

    def disable_tool(self, tool, disabled=True):
        assert tool in self._TOOLS
        self.set_js_property(tool + self._TOOL_DISABLED_SUFFIX, disabled)
        if not disabled:
            self.set_js_property(tool + self._TOOL_ACTIVE_SUFFIX, not disabled)

    def disable_add_tool_for_ball_type(self, ball_type_or_list, disabled=True):
        if isinstance(ball_type_or_list, self.BallType):
            ball_type_or_list = [ball_type_or_list]
        for ball_type in ball_type_or_list:
            assert isinstance(ball_type, self.BallType)
            property_str = self._DISABLE_ADD_FOR_BALL_TEMPLATE.format(ball_type.value)
            self.set_js_property(property_str, disabled)

    def set_property_for_ball_type(self, property_, ball_type, value):
        assert isinstance(ball_type, self.BallType)
        assert property_ in self._BALL_PROPERTIES
        property_str = '{}_{}'.format(property_, ball_type.value)
        return self.set_js_property(property_str, value)

    def set_property_for_ball_to_ball(self, property_, ball_type_a, ball_type_b, value):
        assert isinstance(ball_type_a, self.BallType) and isinstance(ball_type_b, self.BallType)
        assert property_ in self._MULTIBALL_PROPERTIES
        property_str = '{}_{}_{}'.format(property_, ball_type_a.value, ball_type_b.value)
        return self.set_js_property(property_str, value)

    def enable_physics_for_ball_type(self, ball_type_or_list, enable=True):
        if isinstance(ball_type_or_list, self.BallType):
            ball_type_or_list = [ball_type_or_list]
        for ball_type in ball_type_or_list:
            self.set_property_for_ball_type('usePhysics', ball_type, enable)

    def set_socialforce_for_ball_to_ball(self, ball_type_a, ball_type_b, value):
        return self.set_property_for_ball_to_ball('socialForce', ball_type_a, ball_type_b, value)

    def _connect_level_change(self, property_changed_cb, *args):
        def _on_level_changed():
            old_level = self._effective_level
            if old_level != self.get_effective_level():
                property_changed_cb(*args)

        def _on_level_success():
            if self.get_js_property('levelSuccess', False):
                _on_level_changed()

        success_handler = self.connect_object_props_change(self.APP_JS_PARAMS,
                                                           ['levelSuccess'],
                                                           _on_level_success)
        level_handler = self.connect_object_props_change(self.APP_JS_PARAMS,
                                                         ['currentLevel'],
                                                         _on_level_changed)
        return [success_handler, level_handler]

    def connect_props_change(self, obj, props, property_changed_cb, *args):
        props = set(props)
        handlers = []

        if 'effectiveLevel' in props:
            handlers.extend(self._connect_level_change(property_changed_cb, *args))
            props.remove('effectiveLevel')

        if props:
            # Call the base implementation if there are other properties to connect.
            handlers.extend(super().connect_props_change(obj, props, property_changed_cb, *args))

        return handlers

    def reset(self):
        proxy = self.get_gtk_actions_proxy()
        if proxy.props.g_name_owner is None:
            logger.warning('Cannot call reset on Fizzics. It is not running.')
            return

        proxy.call_sync('Activate',
                        GLib.Variant('(sava{sv})', ('reset', (), {})),
                        Gio.DBusCallFlags.NO_AUTO_START,
                        -1, None)


class LightSpeed(App):

    APP_NAME = 'com.endlessm.LightSpeed'

    _POWERUP_TYPES = ['invulnerable', 'blowup', 'upgrade']
    _UPGRADE_TYPES = ['shrink', 'attraction', 'engine']

    _POWERUP_SPAWN_SUFFIX = 'PowerupSpawnCount'
    _POWERUP_PICKED_SUFFIX = 'PowerupPickedCount'
    _POWERUP_ACTIVE_SUFFIX = 'PowerupActivateCount'
    _UPGRADE_ACTIVE_SUFFIX = 'UpgradeActivateCount'

    def __init__(self):
        super().__init__(self.APP_NAME)

        self.POWERUPS_SPAWN_COUNTERS = list(pw + self._POWERUP_SPAWN_SUFFIX
                                            for pw in self._POWERUP_TYPES)

        self.POWERUPS_PICKED_COUNTERS = list(pw + self._POWERUP_PICKED_SUFFIX
                                             for pw in self._POWERUP_TYPES)

        self._gss = None

    @property
    def gss(self):
        if self._gss is None:
            self._gss = GameStateService()
        return self._gss

    def set_level(self, level):
        '''Sets the level to be played (starting from 1).'''

        assert level > 0, 'The level should start from 1.'

        levelCount = self.get_js_property('availableLevels')

        # If there was a problem getting the property, then we just stop here.
        if levelCount is None:
            return False

        if levelCount < level:
            if not self.set_js_property('availableLevels', ('i', level)):
                return False

        return self.set_js_property('startLevel', ('i', level))

    def reveal_topic(self, topic):
        '''Sets a key in the game state so that the given topic ID is revealed
        in Lightspeed's toolbox.'''

        # @todo: we can now use: ToolBoxTopic.reveal()
        self.gss.set('lightspeed.topic.{}'.format(topic), {'visible': True})

    def set_topic_sensitive(self, topic_name, sensitive=True):
        topic = ToolBoxTopic('LightSpeed', topic_name)
        topic.set_sensitive(sensitive=sensitive)

    def _count_properties(self, type_, suffix, *elements):
        assert all(elem in type_ for elem in elements)
        return sum(self.get_js_property(elem + suffix, 0) for elem in elements)

    def powerups_spawned_count(self, *powerups):
        return self._count_properties(self._POWERUP_TYPES, self._POWERUP_SPAWN_SUFFIX, *powerups)

    def powerups_picked_count(self, *powerups):
        return self._count_properties(self._POWERUP_TYPES, self._POWERUP_PICKED_SUFFIX, *powerups)

    def powerups_active_count(self, *powerups):
        return self._count_properties(self._POWERUP_TYPES, self._POWERUP_ACTIVE_SUFFIX, *powerups)

    def upgrades_active_count(self, *upgrades):
        return self._count_properties(self._UPGRADE_TYPES, self._UPGRADE_ACTIVE_SUFFIX, *upgrades)

    def powerups_spawned(self, *powerups):
        return self.powerups_spawned_count(*powerups) > 0

    def powerups_picked(self, *powerups):
        return self.powerups_picked_count(*powerups) > 0

    def powerups_active(self, *powerups):
        return self.powerups_active_count(*powerups) > 0

    def upgrades_active(self, *upgrades):
        return self.upgrades_active_count(*upgrades) > 0

    def get_powerups_spawned_dict(self, *powerups):
        return {pw: self.powerups_spawned(pw) for pw in powerups}

    def get_powerups_picked_dict(self, *powerups):
        return {pw: self.powerups_picked(pw) for pw in powerups}

    def get_powerups_active_dict(self, *powerups):
        return {pw: self.powerups_active(pw) for pw in powerups}

    def get_upgrades_active_dict(self, *upgrades):
        return {up: self.upgrades_active(up) for up in upgrades}
