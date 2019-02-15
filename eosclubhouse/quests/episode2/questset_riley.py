from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode2.hackdex2find import Hackdex2Find
from eosclubhouse.quests.episode2.hackdex2decrypt import Hackdex2Decrypt
from eosclubhouse.quests.episode2.investigation import Investigation
from eosclubhouse.quests.episode2.lightspeedenemyc1 import LightSpeedEnemyC1
from eosclubhouse.quests.episode2.lightspeedenemyc2 import LightSpeedEnemyC2
from eosclubhouse.quests.episode2.breakingin import BreakingIn


class RileyQuestSet(QuestSet):

    __character_id__ = 'riley'
    __position__ = (279, 260)
    __quests__ = [Hackdex2Find, Investigation, Hackdex2Decrypt, LightSpeedEnemyC1,
                  LightSpeedEnemyC2, BreakingIn]

    def __init__(self):
        super().__init__()

    def get_empty_message(self):
        if Registry.get_quest_set_by_name('AdaQuestSet').is_active():
            return QS('NOQUEST_RILEY_ADA')
        if Registry.get_quest_set_by_name('SanielQuestSet').is_active():
            return QS('NOQUEST_RILEY_SANIEL')
        if Registry.get_quest_set_by_name('FaberQuestSet').is_active():
            return QS('NOQUEST_RILEY_FABER')

        return QS('NOQUEST_RILEY_NOTHING')


Registry.register_quest_set(RileyQuestSet)
