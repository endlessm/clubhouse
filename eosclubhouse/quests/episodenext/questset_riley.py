from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.system import GameStateService
from eosclubhouse.quests.episodenext.RileyQuest1 import RileyQuest1


class RileyQuestSet(QuestSet):

    __character_id__ = 'riley'
    __quests__ = [RileyQuest1]

    def __init__(self):
        super().__init__()
        self._gss = GameStateService()
        self._gss.connect('changed', self.update_visibility)
        self.update_visibility(self._gss)

    # Sometimes, characters might 'leave' the Clubhouse for a while - which amounts to hiding them,
    # or their slot might be occupied by a different object in the clubhouse.
    # The latter is different from an asset swap, as the other object can have its own definition
    # and quest set.
    # In all of these cases, we need to provide for setting a character's visibility based on
    # gamestate.
    def update_visibility(self, gss):
        riley_state = self._gss.get('clubhouse.character.Riley')
        # if the state has no data (i.e. is not in the JSON yet) or the state is NOT should_hide,
        # we will show Riley. In case the get fails we will assume false.
        # NOTE: Not sure why the get() has to be validated if we're already short-circuiting on the
        # 'no data' case...
        self.visible = riley_state is None or not riley_state.get('should_hide',
                                                                  value_if_missing=False)


Registry.register_quest_set(RileyQuestSet)
