from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
# from eosclubhouse import logger
from eosclubhouse.quests.episode4.mazept2 import MazePt2
from eosclubhouse.quests.episode4.levihackdex import LeviHackdex
from eosclubhouse.quests.episode4.mazept3 import MazePt3
from eosclubhouse.quests.episode4.mazept4 import MazePt4


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __quests__ = [MazePt2, LeviHackdex, MazePt3, MazePt4]

    def __init__(self):
        super().__init__()


Registry.register_quest_set(AdaQuestSet)
