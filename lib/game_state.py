from typing import NamedTuple

from lib.config import GAME_CONFIG

GameState = NamedTuple(
    "State",
    [
        ("current_scene", dict),
        ("inventory", list),
        ("engine", dict),
        ("story", dict),
        ("feedback", str),
    ],
)

State = GameState(
    current_scene=GAME_CONFIG["initial_scene"],
    inventory=[],
    engine={"describe_current_scene": True, "last_action": None, "turn_count": 0},
    story=GAME_CONFIG["story"],
    feedback="",
)
