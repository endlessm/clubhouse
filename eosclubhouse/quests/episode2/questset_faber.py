
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode2.makerintro import MakerIntro
from eosclubhouse.quests.episode2.stealthdevice import StealthDevice
from eosclubhouse.quests.episode2.makerquest import MakerQuest
from eosclubhouse.quests.episode2.makedevice import MakeDevice


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __position__ = (200, 625)
    __quests__ = [MakerIntro, StealthDevice, MakerQuest, MakeDevice]

    def __init__(self):
        super().__init__()
        first_quest = self.get_quests()[0]
        self.visible = (first_quest.available or first_quest.conf['complete'] or
                        first_quest.is_named_quest_complete('Chore'))

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_FABERL_ADA')
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_FABER_RILEY')
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_FABER_SANIEL')

        return QS('NOQUEST_FABER_NOTHING')


Registry.register_quest_set(FaberQuestSet)
