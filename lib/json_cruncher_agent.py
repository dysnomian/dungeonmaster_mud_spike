import json
import jsonschema
from yaspin import yaspin

from typing import Any, Dict

from lib.config import GAME_CONFIG, client, SCHEMAS_DIR, llm_config_for
from lib.logger import logger
from utils import extract_fenced_json


class JSONCruncher:
    def __init__(self, name="json_cruncher"):
        self.name = name
        self.system_prompt = GAME_CONFIG["agents"][self.name]["system_prompt"]
        self.llm_config = llm_config_for(self.name)
        self.client = client(self.llm_config)

    @yaspin(text="Updating state...", color="red")
    def json_from_text(self, text: str, obj_type: str) -> dict:
        with open(SCHEMAS_DIR / f"{obj_type}_schema.json", "r") as f:
            schema = f.read()

        logger.info(f"Prompting JSONCruncher for type {obj_type} with text: {text}")

        examples = GAME_CONFIG["agents"][self.name]["object_prompts"][obj_type][
            "examples"
        ]

        prompt_text = GAME_CONFIG["agents"][self.name]["object_prompts"][obj_type][
            "user_prompt"
        ]
        prompt_text = prompt_text + f"\n\n{text}\n\nExample {obj_type} object(s):\n\n"
        for example in examples:
            prompt_text += f"```json\n{json.dumps(example, indent=2)}\n```\n\n"

        return self.prompt(prompt_text, schema)

    def prompt(self, prompt_text, schema: str) -> dict:

        response = client(self.llm_config).chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt_text},
            ],
            **self.llm_config,
        )
        if response.choices[0].message.content:
            return self.handle_llm_response(response, schema, prompt_text)
        else:
            raise Exception("No response from LLM.")

    def handle_llm_response(
        self, response, schema: str, prompt_text: str
    ) -> Dict[str, Any]:
        content = response.choices[0].message.content

        content_dict = extract_fenced_json(content)

        try:
            jsonschema.validate(content_dict, json.loads(schema))
            return content_dict
        except jsonschema.ValidationError as e:
            error_response = f"""
            (There was a JSON validation error. Please correct your JSON object and resubmit it. Error message: "{e.message}")

            {prompt_text}
            """
            return self.prompt(error_response, schema)
