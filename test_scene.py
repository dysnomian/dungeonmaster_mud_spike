import json
import jsonschema
import pytest
from lib.scene import Scene

VALID_SCENE = {
    "id": "hallway",
    "title": "Hallway",
    "short_description": "You are in a long, dark hallway.",
    "exits": [
        {"id": "door_1", "direction": "west", "short_description": "Door"},
    ],
}


def test_scene_from_json():
    # Test case 1: Valid JSON
    scene_json1 = json.dumps(VALID_SCENE)
    expected_output1 = VALID_SCENE
    assert Scene.from_json(scene_json1).to_dict() == expected_output1

    # Test case 2: Invalid JSON
    scene_json2 = (
        '{"title": "Hallway", "long_description": "You are in a long, dark hallway."'
    )
    with pytest.raises(Exception):
        Scene.from_json(scene_json2)


def test_scene_from_dict():
    # Test case 1: Valid dictionary
    scene_dict1 = VALID_SCENE
    expected_output1 = VALID_SCENE
    assert Scene.from_dict(scene_dict1).to_dict() == expected_output1

    # Test case 2: Invalid dictionary
    scene_dict2 = VALID_SCENE.copy()
    del scene_dict2["id"]
    with pytest.raises(jsonschema.exceptions.ValidationError):
        Scene.from_dict(scene_dict2)


def test_validate_scene_json():
    # Test case 1: Valid JSON
    scene_json1 = json.dumps(VALID_SCENE)
    assert Scene.validate_scene_json(scene_json1) == True

    # Test case 2: Invalid JSON
    scene_json2 = VALID_SCENE.copy()
    del scene_json2["id"]
    scene_json2 = json.dumps(scene_json2)

    with pytest.raises(jsonschema.exceptions.ValidationError):
        Scene.validate_scene_json(scene_json2)


def test_validate_scene_dict():
    # Test case 1: Valid dictionary
    scene_dict1 = VALID_SCENE
    assert Scene.validate_scene_dict(scene_dict1) == True

    # Test case 2: Invalid dictionary
    scene_dict2 = {
        "title": "Hallway",
        "long_description": "You are in a long, dark hallway.",
    }
    with pytest.raises(Exception):
        Scene.validate_scene_dict(scene_dict2)


def test_format_readable():
    # Test case 1: Scene with title and long description
    scene_json1 = json.dumps(VALID_SCENE)
    expected_output1 = "\x1b[1m\x1b[4mHallway\x1b[0m\nYou are in a long, dark hallway.\n\n\x1b[4mExits:\x1b[0m\n- West: Door\n"
    assert Scene.from_json(scene_json1).format_readable() == expected_output1

    # # Test case 2: Scene with title, long description, and exits
    # scene_json2 = '{"title": "Hallway", "long_description": "You are in a long, dark hallway.", "exits": [{"direction": "north", "short_description": "Door with metal bars"}, {"direction": "south", "short_description": "Wall"}]}'
    # expected_output2 = "Hallway\nYou are in a long, dark hallway.\n\nExits:\n- North: Door with metal bars\n- South: Wall\n"
    # assert Scene.from_json(scene_json2).format_readable() == expected_output2

    # # Test case 3: Scene without title or long description
    # scene_json3 = '{"exits": [{"direction": "north", "short_description": "Door with metal bars"}, {"direction": "south", "short_description": "Wall"}]}'
    # expected_output3 = "\nExits:\n- North: Door with metal bars\n- South: Wall\n"
    # assert Scene.from_json(scene_json3).format_readable() == expected_output3


test_scene_from_json()
test_scene_from_dict()
test_validate_scene_json()
test_validate_scene_dict()
test_format_readable()
