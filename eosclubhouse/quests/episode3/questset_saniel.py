from eosclubhouse.libquest import Registry, QuestSet


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __quests__ = ['SetUp', 'PowerUpA1', 'PowerUpA2', 'PowerUpB1', 'PowerUpB2', 'PowerUpC1',
                  'PowerUpC2', 'PowerUpC3', 'LightspeedFinal', 'ApplyFob2', 'ActivateTrap']


Registry.register_quest_set(SanielQuestSet)
