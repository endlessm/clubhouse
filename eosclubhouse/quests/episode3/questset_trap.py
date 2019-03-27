from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet


class TrapQuestSet(QuestSet):

    __character_id__ = 'trap'
    __position__ = (270, 340)
    __quests__ = []

    def __init__(self):
        super().__init__()

    def get_empty_message(self):
        return QS('NOQUEST_TRAP_NOTHING')


Registry.register_quest_set(TrapQuestSet)
