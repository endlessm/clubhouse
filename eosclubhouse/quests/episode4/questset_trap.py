from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.system import GameStateService
# from eosclubhouse import logger
from eosclubhouse.quests.episode4.trapintro import TrapIntro


class TrapQuestSet(QuestSet):

    __character_id__ = 'trap'
    __quests__ = [TrapIntro]

    def __init__(self):
        super().__init__()

        gss = GameStateService()
        gss.connect('changed', self.update_visibility)
        self.update_visibility(gss)

        super().set_body_animation('transcoding')

    def update_visibility(self, gss):
        trap_state = gss.get('clubhouse.character.Trap')
        # logger.debug('trap deployment state is %s', trap_state)
        # if the trap is NOT deployed, it is visible
        # otherwise, it is hidden
        # this means Riley's space is empty most of the time in ep4
        self.visible = trap_state is None or not trap_state.get('deployed', False)


Registry.register_quest_set(TrapQuestSet)
