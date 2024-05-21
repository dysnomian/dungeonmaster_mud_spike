from typing import Dict, Any
from yaspin import yaspin

from lib.config import GAME_CONFIG, SCHEMAS_DIR
from lib.logger import logger
from lib.color import color
from lib.game_state import GameState, State
from lib.narrator_agent import Narrator


def format_readable_scene(scene: Dict[str, Any]) -> str:
    "Print the scene JSON in a human-readable format."
    scene_description = ""

    if "feedback" in scene:
        scene_description = scene_description + scene["feedback"] + "\n\n"

    if "title" in scene:
        scene_description = (
            scene_description
            + color.bold
            + color.underline
            + scene["title"]
            + color.end
            + "\n"
        )

    scene_description += scene["description"]

    if "exits" in scene:
        scene_description += "\n\n" + color.underline + "Exits:" + color.end + "\n"
        for exit_data in scene["exits"]:
            if "hidden" in exit_data:
                continue
            scene_description += (
                f"- {exit_data['direction'].capitalize()}: {exit_data['description']}\n"
            )

    scene_description += "\nWhat do you do?\n"

    return scene_description


def dispatch_user_action(user_action: str, state: GameState) -> GameState:
    match user_action.split(" ", 1):
        case ["quit"]:
            print("Goodbye!")
            exit(0)
        case ["inventory"]:
            if state.inventory:
                print("Inventory:")
                for item in state.inventory:
                    print(f"- {item}")
            else:
                print("You have no items in your inventory.")
            return state
        case ["look"]:
            return state
        case ["look", *rest]:
            with yaspin(text="Interpreting command...", color="cyan"):
                return Narrator().look_at(" ".join(rest), state)
        case ["go", *rest]:
            with yaspin(text="Generating...", color="cyan"):
                state = Narrator().go(user_action, state)
            return state
        case ["use", *rest]:
            with yaspin(text="Generating...", color="cyan"):
                state = Narrator().use(user_action, state)
            return state
        case [_, *rest]:
            print("Oops! I don't understand that command.")
            return state


def game_loop(state: GameState):
    while True:

        # Show the current scene by default at the top of the loop, unless we set engine.describe_current_scene to False
        if state.engine["describe_current_scene"]:
            print(format_readable_scene(state.current_scene))

        state = GameState(
            current_scene=state.current_scene,
            inventory=state.inventory,
            engine={
                "describe_current_scene": True,
                "last_action": state.engine["last_action"],
            },
            story=state.story,
            feedback="",
        )

        user_action = input("> ")

        state = dispatch_user_action(user_action, state)

        logger.info("State: %s", state)

        state = GameState(
            current_scene=state.current_scene,
            inventory=state.inventory,
            engine={
                "describe_current_scene": state.engine["describe_current_scene"],
                "last_action": user_action,
            },
            story=state.story,
            feedback="",
        )


if __name__ == "__main__":
    game_loop(State)
