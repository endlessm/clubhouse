from eosclubhouse.libquest import Registry, Quest, QuestSet
from eosclubhouse.quests.hackyballs1 import HackyBalls1
from eosclubhouse.quests.hackyballs2 import HackyBalls2
from eosclubhouse.quests.hackyballs3 import HackyBalls3

class TeacherQuestSet(QuestSet):

    __character_id__ = 'teacher'
    __quests__ = [HackyBalls1(), HackyBalls2(), HackyBalls3()]

Registry.register_quest_set(TeacherQuestSet)
