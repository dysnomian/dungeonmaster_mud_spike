"""
The spike! The goal here is just to have a playable game to figure out what needs to go into the bigger game and how the pieces fit together.
"""

from typing import List, Dict

from lib.logger import logger
from lib.agent import Agent
from lib.config import GAME_CONFIG
from lib.game_state import GameState
from scene_describer_agent import SceneDescriberAgent


def action__debug_state(
    action_params: List[str], agent: Agent, state: GameState
) -> GameState:
    logger.info(f"Interpreted user action: {action_params}")
    logger.info(state)
    state.dont_describe_scene()
    return state


def action__inventory(
    action_params: List[str], agent: Agent, state: GameState
) -> GameState:
    logger.info(f"Interpreted user action: {action_params}")
    state.print_inventory()
    state.dont_describe_scene()
    return state


def action__look(action_params: List[str], agent: Agent, state: GameState) -> GameState:
    logger.info(f"Interpreted user action: {action_params}")
    return agent.prompt(
        {
            "user_action": action_params,
            "current_scene": state.current_scene.to_dict(),
            "task": "Create or update the scene's long_description with additional details relevant to the current situation.",
        },
        state,
    )


def handle_user_action(user_action: str, state: GameState, agents: Dict[str, Agent]):
    "Handle the user's action, updating the game state accordingly."
    ### big ol case statement
    logger.info("User action string: %s", user_action)
    action_params = user_action.split(" ", 1)
    match action_params:
        # case ["debug", "state"]:
        #     return action__debug_state(action_params, narrator, state)
        # case ["inventory"]:
        #     return action__inventory(action_params, narrator, state)
        case ["look"]:
            return action__look(action_params, agents["scene_describer"], state)
        # case ["look", *rest]:
        #     logger.info("Interpreted user action: ['look', %s] (%s)", rest, user_action)
        #     updated_state = narrator.prompt(
        #         {
        #             "user_action": user_action,
        #             "task": "Use 'feedback' to describe the thing the user is looking at. Update the relevant description fields for the item, scene, or other if applicable.",
        #         },
        #         State,
        #     )
        #     game_state = updated_state
        #     return
        # case ["go", *rest]:
        #     updated_state = narrator.prompt(
        #         {
        #             "user_action": user_action,
        #             "task": "Evaluate whether it is possible or reasonable for the player to go in the direction they've specified. If it is, generate a new scene based on the user's chosen direction with a new id. Ensure that the route to the previous scene is included in the new scene's exits.",
        #         },
        #         State,
        #     )
        #     game_state = updated_state
        #     return
        # case ["use", *rest]:
        #     updated_state = narrator.prompt(
        #         {
        #             "user_action": user_action,
        #             "task": "Evaluate whether it is possible or reasonable for the player to use the item they've specified. If it is a physical object, ensure it is in their inventory or in the scene. Determine whether their attempt to use it is successful, and describe new scene.",
        #         },
        #         State,
        #     )
        #     game_state = updated_state
        #     return
        case _:
            return agents["scene_describer"].prompt(
                {
                    "user_action": user_action,
                    "task": "Evaluate the user's desired action and respond accordingly. Describe the new scene.",
                },
                State,
            )


def game_loop(state, agents) -> GameState:
    state.increment_turn_count()
    state.display_any_feedback()
    state.describe_current_scene()

    user_action = input("> ")

    print("\n\n")

    if user_action == "quit":
        print("Goodbye!")
        exit(0)

    state = handle_user_action(user_action, state, agents)

    return state


if __name__ == "__main__":
    State = GameState.from_dict(
        {
            "current_scene": GAME_CONFIG["initial_scene"],
            "inventory": GAME_CONFIG.get("inventory"),
            "player": GAME_CONFIG.get("player"),
            "engine": {"describe_current_scene": True, "turn_count": 0},
            "environment": GAME_CONFIG.get("environment"),
        }
    )

    logger.info("Initial game state: %s", State.to_dict())

    agents_list = {
        "narrator": Agent("narrator"),
        "scene_describer": SceneDescriberAgent(),
    }

    while True:
        State = game_loop(State, agents_list)
