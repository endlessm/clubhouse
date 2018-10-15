
from gi.repository import GLib
from eosclubhouse.libquest import Registry, Quest, QuestSet
from eosclubhouse.quests.hackyballs0 import HackyBalls0
from eosclubhouse.quests.hackyballs1 import HackyBalls1



class TeacherQuestSet(QuestSet):

    __character_id__ = 'teacher'
    __quests__ = [HackyBalls0(), HackyBalls1()]


Registry.register_quest_set(TeacherQuestSet)
