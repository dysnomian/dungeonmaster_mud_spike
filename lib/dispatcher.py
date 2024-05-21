import re

from typing import Any, Dict, List

from lib.logger import logger
from lib.json_cruncher_agent import JSONCruncher
from lib.scene_generator_agent import SceneGenerator
from lib.game_state import GameState


def extract_commands(text: str, state: GameState) -> List[Dict[str, Any]]:
    """Extract commands and their parameters from an response. Returns a dictionary of the command, its parameters, and its receiver.

    Examples:

    "<GENERATE SCENE> A library with a giant window, a spiral staircase, two other exits, and a secret map." -> {"command": "generate_scene", "receiver": "SceneDescriber", "parameters": "A library with a giant window, a spiral staircase, two other exits, and a secret map.", "scene": {"id": "scene_name"}}

    "<FEEDBACK> You move the rug and discover a trapdoor! <UPDATE SCENE> Make the trapdoor exit unhidden." -> [{"command": "feedback", "parameters": "You move the rug and discover a trapdoor!"},{"command": "update_scene", "parameters": "Make the trapdoor exit unhidden.", "scene": {"id": "scene_name"}}]
    """

    logger.info("Extracting commands from text: %s", text)
    # Extract all commands bracketed by < > symbols and the text following them through to the end of the line or the next command
    pattern = r"(?s)<(.*?)>\s(.*?)(?=<|$)"

    # Find all matches in the text
    matches = re.findall(pattern, text)

    # Initialize the list of commands
    commands = []

    # For each match, create a dictionary with the command and parameters
    for command, parameters in matches:
        command_dict = {
            "command": command.lower().replace(" ", "_"),
            "parameters": parameters.strip(),
        }
        # If the command is "generate_scene", add the "last_scene" key to the dictionary
        if command_dict["command"] == "generate_scene":
            command_dict["last_scene"] = state.current_scene

        # If the command is "update_scene", add the "scene" key to the dictionary
        if command_dict["command"] == "update_scene":
            command_dict["scene"] = state.current_scene

        # Add the command dictionary to the list of commands
        commands.append(command_dict)

    return commands


def dispatch(text: str, state: GameState) -> GameState:
    commands = extract_commands(text, state)
    logger.info("Commands to dispatch: %s", commands)

    for command in commands:
        state = dispatch_command(command, state)

    return state


def dispatch_command(command_dict: Dict[str, Any], state: GameState) -> GameState:

    match command_dict["command"]:
        case "generate_scene":
            state = SceneGenerator().new_scene(command_dict["parameters"], state)
        case "update_scene":
            state = SceneGenerator().update_scene(command_dict["parameters"], state)
        case "noop":
            pass
        case "feedback":
            state = GameState(
                current_scene=state.current_scene,
                inventory=state.inventory,
                engine=state.engine,
                story=state.story,
                feedback=command_dict["parameters"],
            )
        case "restructure_scene":
            new_scene = JSONCruncher().json_from_text(
                command_dict["parameters"], "scene"
            )
            state = GameState(
                current_scene=new_scene,
                inventory=state.inventory,
                engine=state.engine,
                story=state.story,
                feedback=state.feedback,
            )
        case _:
            raise ValueError(
                f"Dispatcher: Command {command_dict['command']} not recognized."
            )
            return state

    return state
