import json

from typing import Dict, Any

import jsonschema

from lib.logger import logger
from lib.config import client, GAME_CONFIG, SCHEMAS_DIR
from lib.scene import Scene
from lib.agent import Agent
from utils import extract_fenced_json

from lib.game_state import GameState

EXAMPLE_SCENE = GAME_CONFIG["initial_scene"]


class SceneDescriberAgent(Agent):
    def __init__(self, name="scene_describer"):
        self.name = name
        self.response_schema_filename = f"{self.name}_response_schema.json"
        self.response_schema = self.fetch_response_schema()
        self.system_prompt = f"{GAME_CONFIG["agents"][name]["system_prompt"]}\n\n```jsonschema{Scene.schema()}```\n\nHere's an example of valid scene JSON:\n```json\n{EXAMPLE_SCENE}\n```"
        self.llm_config = {
            "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
            "temperature": 0.5,
            "max_tokens": 1000,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "response_format": {"type": "json_object"},
        }

    def prompt(self, prompt_dict: Dict[str, Any], state: GameState) -> GameState:
        "Given prompt text, send it to the LLM. Handle the response with a handler function."

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(prompt_dict),
                },
            ],
            **self.llm_config,
        )
        if response.choices[0].message.content:
            return self.handle_llm_response(response.choices[0].message.content, state)

        raise ValueError("No content in response.")

    # TODO: Implement handle_llm_response
    # Validate the response against the schema
    # Consider grammars?
    def handle_llm_response(self, content_json: str, state: GameState) -> GameState:
        "Take the JSON response from the LLM, parse it, request a do over if the JSON is bad, and update the game state."

        content_dict = {}
        new_state = state

        try:
            content_dict = extract_fenced_json(content_json)

            logger.info("New scene from scene describer: %s", content_dict)
            new_state.update_current_scene(content_dict)

            return new_state

        except jsonschema.exceptions.ValidationError as e:
            logger.error("JSON schema error: %s", e)
            logger.info("Validation errors: %s", e.message)
            logger.info("Response: %s", content_dict)

            error_prompt = {
                "error_type": "JSON validation error (scene)",
                "message": "Sorry, your JSON didn't validate against the scene schema. Please reformat it and try again.",
                "validation_errors": e.message,
                "response": content_dict,
                "schema": Scene.schema(),
            }
            logger.info("Error prompt: %s", error_prompt)
            return self.prompt(error_prompt, state)
        # Sometimes it returns bad JSON. Just ask it to try again.
        except json.JSONDecodeError as e:
            logger.error("JSON decode error: %s", e)
            error_prompt = {
                "error_type": "JSON decode error",
                "message": "Sorry, that JSON was malformed. Please try again.",
                "errors": f"{e}",
                "response": content_json,
            }
            logger.info("Error prompt: %s", error_prompt)
            return self.prompt(error_prompt, state)

    def __str__(self):
        return f"{self.name}: {self.system_prompt}\n\n{self.response_schema_filename}"
