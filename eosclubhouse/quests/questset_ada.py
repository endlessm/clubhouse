from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.roster import Roster
from eosclubhouse.quests.fizzicsintro import FizzicsIntro
from eosclubhouse.quests.osintro import OSIntro


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __quests__ = [Roster(), FizzicsIntro(), OSIntro()]

Registry.register_quest_set(AdaQuestSet)
