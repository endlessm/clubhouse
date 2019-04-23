from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.system import GameStateService
from eosclubhouse.quests.episode2.investigation import Investigation
from eosclubhouse.quests.episode2.lightspeedenemyc1 import LightSpeedEnemyC1
from eosclubhouse.quests.episode2.lightspeedenemyc2 import LightSpeedEnemyC2
from eosclubhouse.quests.episode2.breakingin import BreakingIn


class RileyQuestSet(QuestSet):

    __character_id__ = 'riley'
    __quests__ = [Investigation, LightSpeedEnemyC1,
                  LightSpeedEnemyC2, BreakingIn]

    def __init__(self):
        super().__init__()
        gss = GameStateService()
        gss.connect('changed', self.update_visibility)
        self.update_visibility(gss)

    def update_visibility(self, gss):
        riley_state = gss.get('clubhouse.character.Riley')
        self.visible = riley_state is None or not riley_state.get('in_trap', False)


Registry.register_quest_set(RileyQuestSet)
