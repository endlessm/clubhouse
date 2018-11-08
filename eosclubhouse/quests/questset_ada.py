
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.firstcontact import FirstContact
from eosclubhouse.quests.roster import Roster
from eosclubhouse.quests.fizzicsintro import FizzicsIntro
from eosclubhouse.quests.osintro import OSIntro


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __position__ = (38, 208)
    __quests__ = [FirstContact(), Roster(), FizzicsIntro(), OSIntro()]

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('RickyQuestSet').is_active():
            return QS('NOQUEST_ADA_RICKY')
        if Registry.get_quest_set_by_name('ArchivistQuestSet').is_active():
            return QS('NOQUEST_ADA_ARCHIVER')

        return QS('NOQUEST_ADA_NOTHING')


Registry.register_quest_set(AdaQuestSet)
