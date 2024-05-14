import json
import sys

from typing import Dict, Any

import jsonschema

from lib.logger import logger
from lib.config import client, GAME_CONFIG, SCHEMAS_DIR
from lib.scene import Scene

from lib.game_state import GameState


class Agent:
    def __init__(self, name):
        self.name = name
        self.response_schema_filename = f"{self.name}_response_schema.json"
        self.response_schema = self.fetch_response_schema()
        self.system_prompt = f"{GAME_CONFIG["agents"][name]["system_prompt"]}\n\nllm_response_schema.json:\n{self.response_schema}"
        self.llm_config = {
            "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
            "temperature": 0.2,
            "max_tokens": 500,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "response_format": {"type": "json_object"},
        }

    def fetch_response_schema(self):
        with open(
            SCHEMAS_DIR / self.response_schema_filename, "r", encoding="utf-8"
        ) as f:
            return f.read()

    def default_prompt(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "scene": state["current_scene"],
            "inventory": state["inventory"],
            "environment": state["environment"],
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
            content_dict = json.loads(content_json)

            # Handle 'error' key in response: log it, print it, and exit
            if "error" in content_dict:
                logger.error("LLM raised error: %s", content_dict["error"])
                logger.info("LLM response: %s", content_dict)
                logger.info("Game state: %s", state)
                sys.exit(1)

            # Handle 'feedback' key in response: print it
            if "feedback" in content_dict:
                logger.info("New feedback info from LLM: %s", content_dict["feedback"])
                print(content_dict["feedback"])

            # Handle 'scene' key in response: Create a new Scene object from the dict, validating the scene structure, and update the game state
            if "scene" in content_dict:
                logger.info("New scene from LLM: %s", content_dict["scene"])
                new_state.update_current_scene(content_dict["scene"])

            if "inventory" in content_dict:
                logger.info("New inventory from LLM: %s", content_dict["inventory"])
                new_state.update_inventory(content_dict["inventory"])

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
