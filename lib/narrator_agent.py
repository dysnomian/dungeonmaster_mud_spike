from typing import Tuple

from lib.config import client, llm_config_for, GAME_CONFIG
from lib.dispatcher import dispatch
from lib.game_state import GameState
from utils import scene_to_text


class Narrator:
    def __init__(self, name="narrator"):
        self.name = name
        self.system_prompt = GAME_CONFIG["agents"][self.name]["system_prompt"]
        self.llm_config = llm_config_for(self.name)

    def look_at(self, user_action: str, state: GameState) -> GameState:
        prompt_text = f"The player is in this scene:\n\n{scene_to_text(state.current_scene)}\n\n They want to examine something specific: {user_action}. If that makes sense and is possible, say <FEEDBACK> and give them a more detailed description of whatever they are hoping to examine. If it doesn't make sense or isn't possible, say <FEEDBACK> followed by a brief explanation of why it isn't possible or doesn't make sense. If the examination reveals something new about the scene, say <UPDATE SCENE> followed by a brief updated description of the new scene, being sure to specify what changed in the description."

        return self.prompt(prompt_text, state)

    def go(self, user_action: str, state: GameState) -> GameState:
        prompt_text = f"The player is in this scene:\n\n{scene_to_text(state.current_scene)}\n\n They want to go somewhere: {user_action}. If that is makes sense and is possible, say <FEEDBACK> followed by a brief narration (e.g., 'You go through the north door') then <GENERATE SCENE> followed by a brief description of the new scene that they encounter. If it doesn't make sense, say <FEEDBACK> followed by a brief explanation of why it isn't possible or doesn't make sense."

        return self.prompt(prompt_text, state)

    def use(self, user_action: str, state: GameState) -> GameState:
        prompt_text = f"The player is in this scene:\n\n{scene_to_text(state.current_scene)}\n\n They want to use something: {user_action}. If that is makes sense and is possible, say <FEEDBACK> and describe the outcome of their action. If it doesn't make sense, say <FEEDBACK> followed by a brief explanation of why it isn't possible or doesn't make sense. If the action changes the scene, say <UPDATE SCENE> followed by a brief description of the new scene, being sure to specify what changed in the description."

        return self.prompt(prompt_text, state)

    def prompt(self, prompt_text, state: GameState) -> GameState:
        response = client(self.llm_config).chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt_text},
            ],
            **self.llm_config,
        )
        if response.choices[0].message.content:
            return dispatch(response.choices[0].message.content, state)
        return dispatch(
            "<FEEDBACK> I'm sorry, something went wrong with the narrator agent.",
            state,
        )
