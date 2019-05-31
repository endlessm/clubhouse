from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episodenext.sanielquest1 import SanielQuest1


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __quests__ = [SanielQuest1]

    def __init__(self):
        super().__init__()


Registry.register_quest_set(SanielQuestSet)
