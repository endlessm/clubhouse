from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episodenext.AdaQuest1 import AdaQuest1


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __quests__ = [AdaQuest1]

    def __init__(self):
        super().__init__()


Registry.register_quest_set(AdaQuestSet)
