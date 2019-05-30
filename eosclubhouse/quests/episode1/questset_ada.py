
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __quests__ = ['FirstContact', 'Welcome', 'FizzicsIntro', 'OSIntro', 'Roster', 'LostFiles',
                  'FizzicsCode1']

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('RileyQuestSet').is_active():
            return QS('NOQUEST_ADA_RILEY')
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_ADA_SANIEL')

        quest = self.get_quests()[0]
        if (quest.is_named_quest_complete("FizzicsCode1")):
            return QS('NOQUEST_ADA_CHAPTER1END')

        return QS('NOQUEST_ADA_NOTHING')


Registry.register_quest_set(AdaQuestSet)
