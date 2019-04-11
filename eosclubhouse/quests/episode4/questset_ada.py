
from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode3.rileyslevels import RileysLevels   # this is where we import quests by name, see also below where they are referenced
from eosclubhouse.quests.episode3.applyfob1 import ApplyFob1   # ditto the above


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __position__ = (38, 186)
    __quests__ = [RileysLevels, ApplyFob1]   # change these to include Ada's quests - the class defined in the other py files, see above where we are importing those classes

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_ADA_SANIEL')
        if Registry.get_quest_set_by_name('FaberQuestSet').is_active():
            return QS('NOQUEST_ADA_FABER')

        return QS('NOQUEST_ADA_NOTHING')


Registry.register_quest_set(AdaQuestSet)
