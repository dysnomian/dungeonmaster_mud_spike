import json
import jsonschema

from typing import TYPE_CHECKING, Union, Tuple, Dict, Any

from lib.config import SCHEMAS_DIR, SPEAK_TO_ME, registry
from tts import speak_text
from lib.color import color
from tts import speak_text

from lib.scene import Scene

VALIDATE_WITH_SCHEMA = True
with open(SCHEMAS_DIR / "game_state_schema.json", "r", encoding="utf-8") as f:
    GAME_STATE_SCHEMA = json.load(f)


class GameState:
    @classmethod
    def from_json(cls, game_state_json: str):
        if VALIDATE_WITH_SCHEMA:
            cls.validate_game_state_json(game_state_json)
        return cls(game_state_json)

    @classmethod
    def from_dict(cls, game_state_dict: dict):
        if VALIDATE_WITH_SCHEMA:
            cls.validate_game_state_dict(game_state_dict)
        return cls(json.dumps(game_state_dict))

    @classmethod
    def schema(cls):
        with open(SCHEMAS_DIR / "game_state_schema.json", "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def validator(cls):
        return jsonschema.Draft202012Validator(cls.schema(), registry=registry)

    @classmethod
    def validate_game_state_json(cls, game_state_json: str) -> None:
        "Validate the game state JSON against the schema in game_state_schema.json."
        game_state_dict = json.loads(game_state_json)

        return cls.validator().validate(game_state_dict)

    @classmethod
    def validate_game_state_dict(cls, game_state_dict: dict) -> None:
        "Validate the game state dictionary against the schema in game_state_schema.json."
        return cls.validator().validate(game_state_dict)

    def __init__(self, game_state_json: str):
        self.game_state_dict = json.loads(game_state_json)

    def to_dict(self):
        return self.game_state_dict

    def update(self, update_dict: dict) -> "GameState":
        proposed_state = self.to_dict().update(update_dict)
        GameState.validate_game_state_dict(proposed_state)
        self.game_state_dict = proposed_state
        return self

    def update_current_scene(self, scene_dict: Dict[str, Any]) -> "GameState":
        Scene.validate_scene_dict(scene_dict)
        return self.update({"current_scene": scene_dict})

    def update_inventory(self, inventory: list) -> "GameState":
        return self.update({"inventory": inventory})

    def update_feedback(self, feedback: str) -> "GameState":
        return self.update({"feedback": feedback})

    def update_engine(self, engine_dict: dict) -> "GameState":
        return self.update({"engine": engine_dict})

    def update_environment(self, environment_dict: dict) -> "GameState":
        return self.update({"environment": environment_dict})

    @property
    def current_scene(self) -> "Scene":
        return Scene(self.game_state_dict["current_scene"])

    def describe_current_scene(self) -> None:
        if self.game_state_dict["engine"]["describe_current_scene"]:
            scene_description = self.current_scene.format_readable()
            print(scene_description)

            if SPEAK_TO_ME:
                speak_text(scene_description)

        self.game_state_dict["engine"]["describe_current_scene"] = True

    def dont_describe_scene(self) -> None:
        self.game_state_dict["engine"]["describe_current_scene"] = False

    @property
    def inventory(self) -> list:
        return self.game_state_dict["inventory"]

    def print_inventory(self) -> list:
        if self.inventory:
            print("Inventory:")
            for item in self.inventory:
                print(f"- {item}")
        else:
            print("You have no items in your inventory.")

        return self.inventory

    def display_any_feedback(self) -> None:
        if "feedback" in self.game_state_dict:
            print(color.bold + self.game_state_dict["feedback"] + color.end + "\n\n")
            del self.game_state_dict["feedback"]

    @property
    def turn_count(self) -> int:
        return self.game_state_dict["engine"]["turn_count"]

    def increment_turn_count(self) -> int:
        self.game_state_dict["engine"]["turn_count"] += 1
        return self.turn_count
