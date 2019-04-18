from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode2.chore import Chore
from eosclubhouse.quests.episode2.lightspeedfix1 import LightSpeedFix1
from eosclubhouse.quests.episode2.lightspeedfix2 import LightSpeedFix2
from eosclubhouse.quests.episode2.lightspeedenemyb1 import LightSpeedEnemyB1
from eosclubhouse.quests.episode2.lightspeedenemyb2 import LightSpeedEnemyB2


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __quests__ = [Chore, LightSpeedFix1, LightSpeedFix2, LightSpeedEnemyB1, LightSpeedEnemyB2]


Registry.register_quest_set(SanielQuestSet)
