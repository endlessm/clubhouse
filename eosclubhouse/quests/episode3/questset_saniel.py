from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode3.setup import SetUp
from eosclubhouse.quests.episode3.powerupa1 import PowerUpA1
from eosclubhouse.quests.episode3.powerupa2 import PowerUpA2
from eosclubhouse.quests.episode3.powerupb1 import PowerUpB1
from eosclubhouse.quests.episode3.powerupb2 import PowerUpB2
from eosclubhouse.quests.episode3.powerupc1 import PowerUpC1
from eosclubhouse.quests.episode3.powerupc2 import PowerUpC2
from eosclubhouse.quests.episode3.powerupc3 import PowerUpC3
from eosclubhouse.quests.episode3.lightspeedfinal import LightspeedFinal
from eosclubhouse.quests.episode3.applyfob2 import ApplyFob2
from eosclubhouse.quests.episode3.activatetrap import ActivateTrap


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __quests__ = [SetUp, PowerUpA1, PowerUpA2, PowerUpB1, PowerUpB2, PowerUpC1, PowerUpC2,
                  PowerUpC3, LightspeedFinal, ApplyFob2, ActivateTrap]


Registry.register_quest_set(SanielQuestSet)
