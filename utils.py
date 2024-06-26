import dis
import json

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game_state import GameState


def extract_from_fenced_code_block(text: str, n: int = 0) -> str | None:
    """
    Extract the nth code block from the given text and return it.

    Example `text` inputs:
    "Here is the JSON you asked for:\n\n```json\n{\n\"scene\":\"A new scene\"\n}\n```\n\nI hope this helps."
    "Here is the JSON you asked for:\n\n```\n{\n\"scene\":\"A new scene\"\n}\n```\n\nI hope this helps."
    "```json\n{\n\"scene\":\"A new scene\"\n}\n```"
    "```{\n\"scene\":\"A new scene\"\n}```"
    """

    code_blocks = text.split("```")
    code_blocks = code_blocks[-2::-2]
    if len(code_blocks) > n:
        # if the code block begins with a language specifier, remove it
        language_specifiers = ["json", "python", "yaml"]
        if code_blocks[n].startswith("\n"):
            code_blocks[n] = code_blocks[n][1:]
        for language in language_specifiers:
            if code_blocks[n].startswith(language):
                code_blocks[n] = code_blocks[n][len(language) + 1 :]
                break
        return code_blocks[n].strip()


def extract_fenced_json(text: str) -> dict:
    "Extract the first JSON code block from the given text and return it as a Python dictionary."

    # First, is it actually a dict? Not sure why this happens
    if isinstance(text, dict):
        return text

    # Second, is it already a JSON string?
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    code_block = extract_from_fenced_code_block(text)
    if code_block:
        try:
            return json.loads(code_block)
        except json.JSONDecodeError:
            print("Error decoding JSON code block.")
    return {}


def scene_to_text(scene: dict) -> str:
    "Convert a scene object to a LLM-readable string."
    scene_description = ""

    if "title" in scene:
        scene_description = scene_description + scene["title"] + "\n"

    scene_description += scene["description"]

    if "exits" in scene:
        scene_description += "\n\nExits:\n"
        for exit_data in scene["exits"]:
            if "hidden" in exit_data:
                continue
            scene_description += (
                f"- {exit_data['direction'].capitalize()}: {exit_data['description']}\n"
            )

    if "internal_notes" in scene:
        scene_description += f"\n\nInternal Notes:\n{scene["internal_notes"]}"

    return scene_description
