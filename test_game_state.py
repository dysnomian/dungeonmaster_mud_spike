import pytest

import json
import jsonschema

from lib.game_state import GameState

VALID_GAME_STATE = {
    "player": {
        "name": "John",
        "level": 5,
        "health": 100,
        "inventory": ["sword", "shield"],
    },
    "location": "castle",
    "score": 1000,
}

INVALID_GAME_STATE = {
    "player": {
        "name": "John",
        "level": 5,
        "health": 100,
        "inventory": ["sword", "shield"],
    },
    "location": "castle",
    "score": "1000",  # Invalid type, should be an integer
}


def test_game_state_from_json():
    # Test case 1: Valid JSON
    game_state_json1 = json.dumps(VALID_GAME_STATE)
    expected_output1 = VALID_GAME_STATE
    assert GameState.from_json(game_state_json1).to_dict() == expected_output1

    # Test case 2: Invalid JSON
    game_state_json2 = '{"player": {"name": "John", "level": 5, "health": 100, "inventory": ["sword", "shield"]}, "location": "castle", "score": "1000"}'
    with pytest.raises(jsonschema.exceptions.ValidationError):
        GameState.from_json(game_state_json2)


def test_game_state_from_dict():
    # Test case 1: Valid dictionary
    game_state_dict1 = VALID_GAME_STATE
    expected_output1 = VALID_GAME_STATE
    assert GameState.from_dict(game_state_dict1).to_dict() == expected_output1

    # Test case 2: Invalid dictionary
    game_state_dict2 = INVALID_GAME_STATE
    with pytest.raises(jsonschema.exceptions.ValidationError):
        GameState.from_dict(game_state_dict2)


def test_validate_game_state_json():
    # Test case 1: Valid JSON
    game_state_json1 = json.dumps(VALID_GAME_STATE)
    assert GameState.validate_game_state_json(game_state_json1) == True

    # Test case 2: Invalid JSON
    game_state_json2 = '{"player": {"name": "John", "level": 5, "health": 100, "inventory": ["sword", "shield"]}, "location": "castle", "score": "1000"}'
    with pytest.raises(jsonschema.exceptions.ValidationError):
        GameState.validate_game_state_json(game_state_json2)


def test_validate_game_state_dict():
    # Test case 1: Valid dictionary
    game_state_dict1 = VALID_GAME_STATE
    assert GameState.validate_game_state_dict(game_state_dict1) == True

    # Test case 2: Invalid dictionary
    game_state_dict2 = INVALID_GAME_STATE
    with pytest.raises(jsonschema.exceptions.ValidationError):
        GameState.validate_game_state_dict(game_state_dict2)


def test_update():
    # Test case 1: Valid proposed state
    game_state_json = json.dumps(VALID_GAME_STATE)
    game_state = GameState(game_state_json)
    proposed_state1 = {
        "player": {
            "name": "John",
            "level": 6,
            "health": 90,
            "inventory": ["sword", "shield", "potion"],
        },
        "location": "dungeon",
        "score": 1500,
    }
    expected_output1 = (True, proposed_state1)
    assert game_state.update(proposed_state1) == expected_output1
    assert game_state.to_dict() == proposed_state1

    # Test case 2: Invalid proposed state
    game_state_json = json.dumps(VALID_GAME_STATE)
    game_state = GameState(game_state_json)
    proposed_state2 = {
        "player": {
            "name": "John",
            "level": 6,
            "health": 90,
            "inventory": ["sword", "shield", "potion"],
        },
        "location": "dungeon",
        "score": "1500",  # Invalid type, should be an integer
    }
    expected_output2 = (False, "score should be of type integer")
    assert game_state.update(proposed_state2) == expected_output2
    assert game_state.to_dict() == VALID_GAME_STATE


test_game_state_from_json()
test_game_state_from_dict()
test_validate_game_state_json()
test_validate_game_state_dict()
test_update()
