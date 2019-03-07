import os
import json

from eosclubhouse import config
from eosclubhouse.system import GameStateService


def set_required_game_state():
    json_path = os.path.join(config.EPISODES_DIR, 'game_states', 'episode2.json')
    if not os.path.exists(json_path):
        return
    with open(json_path) as f:
        game_state = json.load(f)
        gss = GameStateService()
        for key, value in game_state.items():
            gss.set(key, value)
