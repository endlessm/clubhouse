from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.demo.fizzics2 import Fizzics2


class RileyQuestSet(QuestSet):

    __character_id__ = 'riley'
    __quests__ = [Fizzics2]


Registry.register_quest_set(RileyQuestSet)
