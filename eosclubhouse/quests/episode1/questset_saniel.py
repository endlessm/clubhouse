
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode1.hackdex1 import Hackdex1


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __position__ = (72, 659)
    __quests__ = [Hackdex1]

    def __init__(self):
        super().__init__()
        first_quest = self.get_quests()[0]
        self.visible = (first_quest.available or first_quest.conf['complete'] or
                        first_quest.is_named_quest_complete('OSIntro'))

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_SANIEL_ADA')
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_SANIEL_RILEY')

        quest = self.get_quests()[0]
        if (quest.is_named_quest_complete("LostFiles")):
            return QS('NOQUEST_SANIEL_CHAPTER1END')

        return QS('NOQUEST_SANIEL_NOTHING')


Registry.register_quest_set(SanielQuestSet)
