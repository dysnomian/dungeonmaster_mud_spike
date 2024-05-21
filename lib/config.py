import os
from pathlib import Path
from xml.etree.ElementInclude import include

import openai
from referencing import Registry, Resource
from referencing.exceptions import NoSuchResource

import yaml
from openai import OpenAI

registry = Registry()

PROJECT_PATH = Path(__file__).resolve().parent.parent.absolute()
MODULE_NAME = os.getenv("CONTENT_MODULE", "default")
MODULE_DIR = PROJECT_PATH / "content_modules" / MODULE_NAME
GAME_CONFIG = yaml.safe_load(open(f"{MODULE_DIR}/config.yml", "r", encoding="utf-8"))
SCHEMAS_DIR = MODULE_DIR / "schemas"


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_BASE_URL = "http://localhost:1234/v1"  # for LM Studio
API_KEY = "lm-studio"

SPEAK_TO_ME = True if os.getenv("SPEAK_TO_ME") == "true" else False

local_client = OpenAI(base_url=LLM_BASE_URL, api_key=API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def client(llm_config: dict = {}) -> OpenAI:
    openai_models = ["gpt-3.5-turbo", "gpt-4-turbo", "gpt-4", "gpt-4o"]

    if llm_config.get("model") in openai_models:
        return openai_client
    return local_client


def llm_config_for(agent_name: str) -> dict:
    default_config = {
        "model": "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        "temperature": 0.1,
        "max_tokens": 500,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }

    llm_config = GAME_CONFIG["agents"][agent_name]

    return {
        "model": llm_config.get("model", default_config["model"]),
        "temperature": llm_config.get("temperature", default_config["temperature"]),
        "max_tokens": llm_config.get("max_tokens", default_config["max_tokens"]),
        "top_p": llm_config.get("top_p", default_config["top_p"]),
        "frequency_penalty": llm_config.get(
            "frequency_penalty", default_config["frequency_penalty"]
        ),
        "presence_penalty": llm_config.get(
            "presence_penalty", default_config["presence_penalty"]
        ),
    }
