from eosclubhouse.libquest import CharacterMission, Registry


class SanielMission(CharacterMission):

    __character_id__ = 'saniel'


Registry.register_quest_set(SanielMission)
