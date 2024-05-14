import json
import jsonschema

from typing import Union, Literal, Dict, Any

from lib.logger import logger
from lib.color import color
from lib.config import SCHEMAS_DIR, registry

VALIDATE_WITH_SCHEMA = True


class Scene:
    @classmethod
    def from_json(cls, scene_json: str):
        if VALIDATE_WITH_SCHEMA:
            cls.validate_scene_json(scene_json)
        return cls(scene_json)

    @classmethod
    def from_dict(cls, scene_dict: dict):
        if VALIDATE_WITH_SCHEMA:
            cls.validate_scene_dict(scene_dict)
        return cls(json.dumps(scene_dict))

    @classmethod
    def schema(cls):
        with open(SCHEMAS_DIR / "scene_schema.json", "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def validator(cls):
        return jsonschema.Draft202012Validator(cls.schema(), registry=registry)

    @classmethod
    def validate_scene_json(cls, scene_json: str) -> bool:
        "Validate the scene JSON against the schema in scene_schema.json."
        scene_dict = json.loads(scene_json)

        cls.validator().validate(scene_dict)

        return True

    @classmethod
    def validate_scene_dict(cls, scene_dict: dict) -> bool:
        "Validate the scene dictionary against the schema in scene_schema.json."
        cls.validator().validate(scene_dict)

        return True

    def __init__(self, scene_input: Union[str, Dict[str, Any]]):
        self.scene_dict = {}

        if isinstance(scene_input, str):
            self.scene_dict = json.loads(scene_input)
        elif isinstance(scene_input, dict):
            self.scene_dict = scene_input
        else:
            raise ValueError(f"Invalid scene_input type: {type(scene_input)}")

    def to_dict(self):
        return self.scene_dict

    def description(
        self, length: Union[Literal["short"], Literal["long"]] = "short"
    ) -> str:
        "Return the short or long description of the scene."
        if length == "short":
            return self.scene_dict["short_description"]
        elif length == "long":
            return self.scene_dict["long_description"]
        else:
            raise ValueError(f"Invalid description length type: {length}")

    def format_readable(self) -> str:
        "Print the scene JSON in a human-readable format."
        logger.info("Formatting scene: %s", self.scene_dict)
        scene_description = ""

        if "title" in self.scene_dict:
            scene_description = (
                scene_description
                + color.bold
                + color.underline
                + self.scene_dict["title"]
                + color.end
                + "\n"
            )

        scene_description += self.scene_dict["description"]

        if "exits" in self.scene_dict:
            scene_description += "\n" + color.underline + "Exits:" + color.end + "\n"
            for exit_data in self.scene_dict["exits"]:
                if "hidden" in exit_data:
                    continue
                scene_description += f"- {exit_data['direction'].capitalize()}: {exit_data['description']}\n"

        return scene_description
