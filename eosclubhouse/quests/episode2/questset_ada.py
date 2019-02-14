
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode2.lightspeedintro import LightSpeedIntro


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __position__ = (38, 206)
    __quests__ = [LightSpeedIntro]

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_ADA_RILEY')
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_ADA_SANIEL')
        if Registry.get_quest_set_by_name('FaberQuestSet').is_active():
            return QS('NOQUEST_ADA_FABER')

        return QS('NOQUEST_ADA_NOTHING')


Registry.register_quest_set(AdaQuestSet)
