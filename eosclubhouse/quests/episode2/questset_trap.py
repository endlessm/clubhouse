from eosclubhouse.utils import QS
from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.system import GameStateService


class TrapQuestSet(QuestSet):

    __character_id__ = 'trap'
    __position__ = (209, 260)
    __quests__ = []

    def __init__(self):
        super().__init__()
        gss = GameStateService()
        gss.connect('changed', self.update_visibility)
        self.update_visibility(gss)

    def update_visibility(self, gss):
        riley_state = gss.get('clubhouse.character.Riley')
        self.visible = riley_state is not None and riley_state.get('in_trap', False)

    def get_empty_message(self):
        return QS('NOQUEST_TRAP_NOTHING')


Registry.register_quest_set(TrapQuestSet)
