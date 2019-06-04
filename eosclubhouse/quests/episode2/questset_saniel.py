from eosclubhouse.libquest import Registry, QuestSet


class SanielQuestSet(QuestSet):

    __character_id__ = 'saniel'
    __quests__ = ['Chore', 'LightSpeedFix1', 'LightSpeedFix2', 'LightSpeedEnemyB1',
                  'LightSpeedEnemyB2']


Registry.register_quest_set(SanielQuestSet)
