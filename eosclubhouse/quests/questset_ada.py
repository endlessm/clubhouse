
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.firstcontact import FirstContact
from eosclubhouse.quests.roster import Roster
from eosclubhouse.quests.fizzicsintro import FizzicsIntro
from eosclubhouse.quests.osintro import OSIntro


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __position__ = (60, 150)
    __quests__ = [FirstContact(), Roster(), FizzicsIntro(), OSIntro()]

    def get_empty_message(self):
        quest = self.get_quests()[0]
        if (quest.is_named_quest_complete("OSIntro") and
            (not quest.is_named_quest_complete("Fizzics1") or
             not quest.is_named_quest_complete("BreakSomething") or
             not quest.is_named_quest_complete("Fizzics2"))):
            return QS('NOQUEST_ADA_RICKY')
        if quest.is_named_quest_complete("BreakSomething") and \
           not quest.is_named_quest_complete("HackdexCorruption"):
            return QS('NOQUEST_ADA_ARCHIVER')

        return QS('NOQUEST_ADA_NOTHING')


Registry.register_quest_set(AdaQuestSet)
