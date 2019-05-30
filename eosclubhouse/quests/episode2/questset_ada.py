
from eosclubhouse.libquest import Registry, QuestSet


class AdaQuestSet(QuestSet):

    __character_id__ = 'ada'
    __quests__ = ['LightSpeedIntro', 'LightSpeedTweak', 'LightSpeedEnemyA1', 'LightSpeedEnemyA2',
                  'LightSpeedEnemyA3']


Registry.register_quest_set(AdaQuestSet)
