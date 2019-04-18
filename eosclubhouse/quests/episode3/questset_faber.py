
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode3.fizzicspuzzle1 import FizzicsPuzzle1
from eosclubhouse.quests.episode3.fizzicspuzzle2 import FizzicsPuzzle2
from eosclubhouse.quests.episode3.applyfob3 import ApplyFob3


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __quests__ = [FizzicsPuzzle1, FizzicsPuzzle2, ApplyFob3]

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_FABER_ADA')
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_FABER_SANIEL')

        return QS('NOQUEST_FABER_NOTHING')


Registry.register_quest_set(FaberQuestSet)
