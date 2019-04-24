from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode4.lightspeedkey import LightspeedKey


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __quests__ = [LightspeedKey]

    def __init__(self):
        super().__init__()


Registry.register_quest_set(FaberQuestSet)
