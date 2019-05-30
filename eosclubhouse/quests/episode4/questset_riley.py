from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.system import GameStateService


class RileyQuestSet(QuestSet):

    __character_id__ = 'riley'
    __quests__ = ['BonusRound']

    def __init__(self):
        super().__init__()
        self._gss = GameStateService()
        self._gss.connect('changed', self.update_visibility)
        self.update_visibility(self._gss)

    def update_visibility(self, gss):
        riley_state = self._gss.get('clubhouse.character.Riley')
        # if the trap is deployed Riley is not necessarily visible
        # we set her as visible in MazePt4
        self.visible = riley_state is None or not riley_state.get('in_trap', False)


Registry.register_quest_set(RileyQuestSet)
