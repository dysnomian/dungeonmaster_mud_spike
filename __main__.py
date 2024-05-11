import os
from pathlib import Path
import json
from typing import NamedTuple

from openai import OpenAI
import subprocess


client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SPEAK_TO_ME = True


def speak_text(text: str):
    with openai_client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=text,
    ) as response:
        file_path = Path("speech.mp3")
        response.stream_to_file(file_path)
        subprocess.run(["afplay", file_path])


actions = {
    "look": "Describe the room. Mention obvious exits, items, creatures, and features.",
    "go": "Move the player to a different room. Describe the new room.",
    "take": "Pick up an item in the room.",
    "use": "Use an item in the room.",
    "inventory": "List the items the player has.",
}

initial_scene = """
You are in a torch-lit room. There is a locked door with metal bars in front of you. Behind you is another door.

Obvious exits:
- North: Door with metal bars
- South: Door

What do you do?

"""


def prompt(prompt_text):
    system_prompt = """
    You are a narrator for an old-school text-based adventure game. You will be given a scene and a user action. Evaluate whether they can take the action, and describe the next scene.

    Respond with a JSON object containing the following keys:
    - 'scene': a string describing the new scene. This will be visible to the user at the start of the next turn. Omitting this key means the scene remains unchanged.
    - 'inventory': (optional) A list of strings representing items the player has picked up. Omitting this key means the player's inventory remains unchanged. This will replace their existing inventory, so don't forget to include items they already had.
    Don't forget to escape line breaks and special characters in your JSON string.
    """

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text},
        ],
        model="lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF",
        temperature=0.2,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format={"type": "json"},
    )
    if response.choices[0].message.content:
        return handle_llm_response(response)
    return "No description generated."


game_state = {
    "current_scene": initial_scene,
    "player": {
        "name": "Tara",
        "health": 100,
        "inventory": [],
    },
    "engine": {
        "describe_current_scene": True,
        "last_action": None,
    },
}


def handle_llm_response(response):
    try:
        content = json.loads(response.choices[0].message.content)

        if "scene" in content:
            game_state["current_scene"] = content["scene"]
        if "inventory" in content:
            game_state["player"]["inventory"] = content["inventory"]
    except json.JSONDecodeError:
        prompt(
            "Sorry, that JSON didn't parse correctly. Please try again. Here's what I received: "
            + response.choices[0].message.content
        )


def game_loop():
    while True:

        if game_state["engine"]["describe_current_scene"]:
            print(game_state.get("current_scene"))

        game_state["engine"]["describe_current_scene"] = True

        user_action = input("> ")

        if SPEAK_TO_ME:
            speak_text(str(game_state.get("current_scene")))

        print("\n\n")

        ### big ol case statement
        match user_action.split(" ", 1):
            case ["debug", "state"]:
                print(json.dumps(game_state, indent=4))
                game_state["engine"]["describe_current_scene"] = False
                continue
            case ["quit"]:
                print("Goodbye!")
                break
            case ["help"]:
                print("Actions:")
                for action, description in actions.items():
                    print(f"{action}: {description}")
                game_state["engine"]["describe_current_scene"] = False
                continue
            case ["inventory"]:
                if game_state["player"]["inventory"]:
                    print("Inventory:")
                    for item in game_state["player"]["inventory"]:
                        print(f"- {item}")
                else:
                    print("You have no items in your inventory.")
                game_state["engine"]["describe_current_scene"] = False
                continue
            case ["look"]:
                prompt(
                    f"The player is in this scene: '{game_state["current_scene"]}'. They want to take this action: '{user_action}' They have the following items: {game_state["player"]["inventory"]} Please describe the current scene in more detail scene for the user."
                )
                continue
            case ["look", *rest]:
                prompt(
                    f"The player is in this scene: '{game_state["current_scene"]}'. They want to take this action: '{user_action}' They have the following items: {game_state['player']['inventory']} Please describe current in more detail scene for the user."
                )
                continue
            case ["go", *rest]:
                prompt(
                    f"The player is in this scene: '{game_state["current_scene"]}'. They want to take this action: '{user_action}' They have the following items: {game_state['player']['inventory']} Please describe the new scene for the user."
                )
                continue
            case ["use", *rest]:
                prompt(
                    f"The player is in this scene: '{game_state["current_scene"]}'. They want to take use this: {rest} They have the following items: {game_state['player']['inventory']} Evaluate whether using that is possible or reasonable given the circumstances, and if so, describe what happens when they attempt it."
                )
                continue
            case [_, *rest]:
                prompt(
                    f"The player is in this scene: '{game_state["current_scene"]}'. They want to take this action: '{user_action}' They have the following items: {game_state['player']['inventory']} Evaluate the action they want to do to decide if it's possible or reasonable given the circumstances, and if so, describe what happens when they attempt it. Please describe the new scene for the user."
                )
                continue

        game_state["engine"]["last_action"] = user_action


if __name__ == "__main__":
    game_loop()
