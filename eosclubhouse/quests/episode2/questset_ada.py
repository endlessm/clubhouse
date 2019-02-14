
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode2.lightspeedintro import LightSpeedIntro


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __position__ = (38, 206)
    __quests__ = [LightSpeedIntro]

    def get_empty_message(self):
        return QS('NOQUEST_ADA_NOTHING')


Registry.register_quest_set(AdaQuestSet)
