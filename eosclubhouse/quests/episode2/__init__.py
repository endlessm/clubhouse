from eosclubhouse.quests.episode1.questset_ada import AdaQuestSet
from eosclubhouse.quests.episode1.questset_riley import RileyQuestSet
from eosclubhouse.quests.episode1.questset_saniel import SanielQuestSet
from eosclubhouse.system import GameStateService

REQUIRED_GAME_STATE = {
    'item.key.fizzics.1': {
        'consume_after_use': False,
        'used': True,
    },
    'item.key.OperatingSystemApp.1': {
        'consume_after_use': False,
        'used': True,
    },
    'item.key.hackdex1.1': {
        'consume_after_use': False,
        'used': False,
    },
    'item.key.fizzics.2': {
        'consume_after_use': False,
        'used': True,
    },
    'lock.OperatingSystemApp.1': {
        'locked': False,
    },
    'lock.fizzics.1': {
        'locked': False,
    },
    'lock.com.endlessm.Hackdex_chapter_one.1': {
        'locked': False,
    },
    'lock.fizzics.2': {
        'locked': False,
    },
}


def set_required_game_state():
    for quest_set in [AdaQuestSet, RileyQuestSet, SanielQuestSet]:
        for quest_class in quest_set.__quests__:
            quest = quest_class()
            quest.complete = True
            quest.save_conf()

    gss = GameStateService()
    for key, value in REQUIRED_GAME_STATE.items():
        gss.set(key, value)
