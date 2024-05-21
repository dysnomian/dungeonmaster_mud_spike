from lib.config import GAME_CONFIG, llm_config_for, client


class Plotter:
    def __init__(self, name="plotter"):
        self.name = name
        self.system_prompt = GAME_CONFIG["agents"][self.name]["system_prompt"]
        self.llm_config = llm_config_for(self.name)

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
        logger.info(f"Plotter response: {content}")

        new_story = JSONCruncher().json_from_text(content, "story")

        return GameState(
            current_scene=state.current_scene,
            inventory=state.inventory,
            engine=state.engine,
            story=new_story,
            feedback="",
        )
