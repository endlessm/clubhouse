from eosclubhouse.libquest import Registry, QuestSet
from eosclubhouse.quests.episode2.makerintro import MakerIntro
from eosclubhouse.quests.episode2.stealthdevice import StealthDevice
from eosclubhouse.quests.episode2.makerquest import MakerQuest
from eosclubhouse.quests.episode2.makedevice import MakeDevice


class FaberQuestSet(QuestSet):

    __character_id__ = 'faber'
    __quests__ = [MakerIntro, StealthDevice, MakerQuest, MakeDevice]

    def __init__(self):
        super().__init__()
        first_quest = self.get_quests()[0]
        self.visible = (first_quest.available or first_quest.conf['complete'] or
                        first_quest.is_named_quest_complete('Investigation'))


Registry.register_quest_set(FaberQuestSet)
