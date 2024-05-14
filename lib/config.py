import os
import json
from pathlib import Path

from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

import yaml
from openai import OpenAI

from lib.logger import logger

registry = Registry()

PROJECT_PATH = Path(__file__).resolve().parent.parent.absolute()
MODULE_NAME = os.getenv("CONTENT_MODULE", "default")
MODULE_DIR = PROJECT_PATH / "content_modules" / MODULE_NAME
GAME_CONFIG = yaml.safe_load(open(f"{MODULE_DIR}/config.yml", "r", encoding="utf-8"))
SCHEMAS_DIR = MODULE_DIR / "schemas"


def retrieve_schema_from_filesystem(uri: str):
    if not uri.startswith("urn:"):
        logger.error("URI does not start with urn: %s", uri)
        raise NoSuchResource(ref=uri)
    path = SCHEMAS_DIR / Path(uri.removeprefix("urn:"))
    contents = json.loads(path.read_text())
    return Resource.from_contents(contents)


registry = Registry(retrieve=retrieve_schema_from_filesystem)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_BASE_URL = "http://localhost:1234/v1"  # for LM Studio
API_KEY = "lm-studio"

SPEAK_TO_ME = True if os.getenv("SPEAK_TO_ME") == "true" else False

client = OpenAI(base_url=LLM_BASE_URL, api_key=API_KEY)


logger.info(
    "Game configuration:\nOpenAI API Key: %s\nBase URL: %s\nAPI Key: %s",
    OPENAI_API_KEY,
    LLM_BASE_URL,
    API_KEY,
)
