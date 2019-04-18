from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode3.fizzicspuzzle1 import FizzicsPuzzle1
from eosclubhouse.quests.episode3.fizzicspuzzle2 import FizzicsPuzzle2
from eosclubhouse.quests.episode3.applyfob3 import ApplyFob3


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __quests__ = [FizzicsPuzzle1, FizzicsPuzzle2, ApplyFob3]


Registry.register_quest_set(FaberQuestSet)
