
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode2.makerintro import MakerIntro


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __position__ = (200, 680)
    __quests__ = [MakerIntro]

    def __init__(self):
        super().__init__()

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_FABERL_ADA')
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_FABER_RILEY')
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_FABER_SANIEL')

        return QS('NOQUEST_FABER_NOTHING')


Registry.register_quest_set(FaberQuestSet)
