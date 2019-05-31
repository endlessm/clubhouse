from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episodenext.faberquest1 import FaberQuest1


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __quests__ = [FaberQuest1]

    def __init__(self):
        super().__init__()


Registry.register_quest_set(FaberQuestSet)
