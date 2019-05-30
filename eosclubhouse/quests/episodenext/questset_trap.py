from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.system import GameStateService
from eosclubhouse.quests.episodenext.TrapQuest1 import TrapQuest1


class TrapQuestSet(QuestSet):

    __character_id__ = 'trap'
    __quests__ = [TrapQuest1]

    def __init__(self):
        super().__init__()

        gss = GameStateService()
        gss.connect('changed', self.update_visibility)
        self.update_visibility(gss)
        # You can set arbitrary animations for characters in the Clubhouse.
        # This is currently only used for characters that have specific animations
        # tied to gamestate progression - like the Trap.
        super().set_body_animation('transcoding')

    def update_visibility(self, gss):
        trap_state = gss.get('clubhouse.character.Trap')
        # if the state has no data (i.e. is not in the JSON yet) or the state is NOT deployed,
        # we will show the Trap. In case the get fails we will assume false.
        # This is the converse of the code in questset_riley.py - both cases must be handled
        # in their individual quest sets.
        self.visible = trap_state is None or not trap_state.get('deployed', False)


Registry.register_quest_set(TrapQuestSet)
