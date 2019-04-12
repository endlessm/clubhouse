from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.system import GameStateService


class TrapQuestSet(QuestSet):

    __character_id__ = 'trap'
    __quests__ = []

    @classmethod
    def get_gss_key(class_):
        return 'clubhouse.character.' + class_.__character_id__.capitalize()

    def __init__(self):
        super().__init__()

        gss = GameStateService()
        character_state = gss.get(self.get_gss_key(), {})
        body_animation = character_state.get('body-animation')
        if body_animation is not None:
            self.body_animation = body_animation

    def get_empty_message(self):
        return QS('NOQUEST_TRAP_NOTHING')


Registry.register_quest_set(TrapQuestSet)
