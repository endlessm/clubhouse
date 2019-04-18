from gi.repository import GLib
from eosclubhouse import logger
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.system import GameStateService, Sound
from eosclubhouse.utils import QS, ClubhouseState


class TrapQuestSet(QuestSet):

    __character_id__ = 'trap'
    __quests__ = []

    @classmethod
    def get_gss_key(class_):
        return 'clubhouse.character.' + class_.__character_id__.capitalize()

    def __init__(self):
        super().__init__()

        self._gss = GameStateService()
        character_state = self._gss.get(self.get_gss_key(), {})

        # Sounds UUIDs by animation-id.
        self._body_animation_sounds = {}
        ClubhouseState().connect('notify::window-is-visible',
                                 self._on_clubhouse_window_visibility_changed_cb)

        body_animation = character_state.get('body-animation')
        if body_animation is not None:
            super().set_body_animation(body_animation)

    def set_body_animation(self, body_animation):
        self._gss.update(self.get_gss_key(),
                         {'body-animation': body_animation}, {})
        super().set_body_animation(body_animation)
        self._play_animation_sounds()

    def get_empty_message(self):
        return QS('NOQUEST_TRAP_NOTHING')

    def _play_animation_sounds(self):
        if not ClubhouseState().window_is_visible:
            return

        def play_animation_sound(sound_event_id):
            if self.body_animation in self._body_animation_sounds:
                self._unmute_animation_sounds()
            else:
                Sound.play(sound_event_id, self._animation_sound_cb, self.body_animation)

        self._stop_previous_animation_sounds()
        if self.body_animation == 'transcoding-init':
            play_animation_sound('quests/episode3/activatetrap/transcoding-init/blowup')
            play_animation_sound('quests/episode3/activatetrap/transcoding-init/pulse')
        elif self.body_animation == 'transcoding':
            play_animation_sound('quests/episode3/activatetrap/transcoding/pulse')

    def _stop_previous_animation_sounds(self):
        for body_animation in list(self._body_animation_sounds.keys()):
            if self.body_animation == body_animation:
                continue
            for uuid in self._body_animation_sounds[body_animation]:
                Sound.stop(uuid)
            del self._body_animation_sounds[body_animation]

    def _mute_animation_sounds(self):
        self._change_animation_sound_volume(0)

    def _unmute_animation_sounds(self):
        self._change_animation_sound_volume(1)

    def _change_animation_sound_volume(self, volume):
        if self.body_animation not in self._body_animation_sounds:
            return

        sounds = self._body_animation_sounds.get(self.body_animation, [])
        if not sounds:
            return

        silence_props = {'volume': GLib.Variant('d', volume)}
        for uuid in sounds:
            Sound.update_properties(uuid, 100, silence_props)

    def _on_clubhouse_window_visibility_changed_cb(self, state, _param):
        if state.window_is_visible:
            self._play_animation_sounds()
        else:
            self._mute_animation_sounds()

    def _animation_sound_cb(self, _proxy, result, animation_id):
        if isinstance(result, GLib.Error):
            logger.warning('Error when attempting to play sound: %s', result.message)
            return
        if animation_id not in self._body_animation_sounds:
            self._body_animation_sounds[animation_id] = set()
        self._body_animation_sounds[animation_id].add(result)


Registry.register_quest_set(TrapQuestSet)
