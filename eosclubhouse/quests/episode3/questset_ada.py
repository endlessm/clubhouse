from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode3.rileyslevels import RileysLevels
from eosclubhouse.quests.episode3.applyfob1 import ApplyFob1


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __quests__ = [RileysLevels, ApplyFob1]


Registry.register_quest_set(AdaQuestSet)
