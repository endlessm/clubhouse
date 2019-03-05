
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode1.firstcontact import FirstContact
from eosclubhouse.quests.episode1.roster import Roster
from eosclubhouse.quests.episode1.fizzicsintro import FizzicsIntro
from eosclubhouse.quests.episode1.osintro import OSIntro
from eosclubhouse.quests.episode1.lostfiles import LostFiles
from eosclubhouse.quests.episode1.fizzicscode1 import FizzicsCode1
from eosclubhouse.quests.episode1.welcome import Welcome


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __position__ = (38, 206)
    __quests__ = [FirstContact, Welcome, FizzicsIntro, OSIntro, Roster, LostFiles, FizzicsCode1]

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
