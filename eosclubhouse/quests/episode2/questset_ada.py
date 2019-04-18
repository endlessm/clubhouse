
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode2.lightspeedintro import LightSpeedIntro
from eosclubhouse.quests.episode2.lightspeedtweak import LightSpeedTweak
from eosclubhouse.quests.episode2.lightspeedenemya1 import LightSpeedEnemyA1
from eosclubhouse.quests.episode2.lightspeedenemya2 import LightSpeedEnemyA2
from eosclubhouse.quests.episode2.lightspeedenemya3 import LightSpeedEnemyA3


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __quests__ = [LightSpeedIntro, LightSpeedTweak, LightSpeedEnemyA1, LightSpeedEnemyA2,
                  LightSpeedEnemyA3]


Registry.register_quest_set(AdaQuestSet)
