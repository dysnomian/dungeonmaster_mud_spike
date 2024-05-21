from lib.config import GAME_CONFIG, llm_config_for, client
from lib.game_state import GameState
from lib.logger import logger
from lib.json_cruncher_agent import JSONCruncher
from utils import scene_to_text


class SceneGenerator:
    def __init__(self, name="scene_generator"):
        self.name = name
        self.llm_config = llm_config_for(self.name)

    @property
    def system_prompt(self) -> str:
        system_prompt = GAME_CONFIG["agents"][self.name]["system_prompt"]
        examples = GAME_CONFIG["agents"][self.name]["examples"]
        for example in examples:
            system_prompt += f"\n\n{example}"
        return system_prompt

    def new_scene(self, description: str, state: GameState) -> GameState:
        user_prompt = f"Here is the general description of the new scene to generate:\n\n{description}/n/nHere is the last scene: {scene_to_text(state.current_scene)}\n\nPlease provide a full description of the new scene."

        return self.prompt(user_prompt, state)

    def update_scene(self, description: str, state: GameState) -> GameState:
        user_prompt = f"This is the current scene:\n\n{scene_to_text(state.current_scene)}\n\nHere is the general idea of the updates to make to the scene:\n\n{description} Please provide a full description of the updated scene."

        return self.prompt(user_prompt, state)

    def prompt(self, prompt_text, state: GameState) -> GameState:
        response = client(self.llm_config).chat.completions.create(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt_text},
            ],
            **self.llm_config,
        )
        if response.choices[0].message.content:
            content = response.choices[0].message.content
            return self.handle_llm_response(content, state)
        return state

    def handle_llm_response(self, content: str, state: GameState) -> GameState:
        logger.info("SceneGenerator response: %s", content)
        new_scene = JSONCruncher().json_from_text(content, "scene")
        logger.info("New scene: %s", new_scene)

        return GameState(
            current_scene=new_scene,
            inventory=state.inventory,
            engine=state.engine,
            story=state.story,
            feedback="",
        )
