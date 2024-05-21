from lib.game_state import GameState

valid_scene = {
    "id": "starting_room",
    "title": "Starting Room",
    "summary": "You are in a small room with a door with metal bars.",
    "description": "You are in a torch-lit room. The floor is moldering wood, and there are no windows. There is a locked door with metal bars. Behind you is another door.",
    "number_of_visits": 0,
    "exits": [
        {
            "id": "door_1",
            "direction": "north",
            "description": "Door with metal bars",
            "locked": True,
        },
        {"id": "door_2", "direction": "south", "description": "Wooden door"},
        {
            "id": "trapdoor_1",
            "direction": "down",
            "description": "Hidden trapdoor under rug",
            "hidden": True,
        },
    ],
}

valid_story = story = {
    "main_quest": "Escape from the mad sorcerer Vraylar.",
    "story": "You are an adventurer trapped in the dungeon of the mad sorcerer Vraylar. You must escape before he sacrifices you to his dark gods. The dungeon is filled with traps and monsters, and surrounded by a dark forest.",
    "goals": [
        "Escape the dungeon.",
        "Find a way out of the tower. (Through the gate, over the wall, or down the secret passage)",
        "Cross the moat.",
        "Make it through the dark forest to the nearest village.",
    ],
    "obstacles": [
        "Locked doors, traps, and secret passages in the dungeon.",
        "The sorcerer's minions and magical guardians.",
        "The moat filled with crocodiles.",
        "The dark forest filled with werewolves and a patrol of ogres hunting you.",
    ],
}

valid_game_state = GameState(
    current_scene=valid_scene,
    inventory=[],
    engine={"describe_current_scene": True, "last_action": None, "turn_count": 0},
    story=valid_story,
    feedback="",
)
