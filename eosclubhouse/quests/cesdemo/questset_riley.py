from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.cesdemo.fizzics2 import Fizzics2


class RileyQuestSet(QuestSet):

    __character_id__ = 'riley'
    __quests__ = [Fizzics2]


Registry.register_quest_set(RileyQuestSet)
