import os
import sys
from unittest.mock import call, patch

import pytest


script_dir = os.path.dirname(__file__)
root_dir = os.path.abspath(os.path.join(script_dir, ".."))
sys.path.append(root_dir)

from unittest.mock import patch


from lib.dispatcher import extract_commands, dispatch_command, dispatch
from lib.game_state import GameState
from lib.config import GAME_CONFIG
from lib.scene_generator_agent import SceneGenerator
from lib.json_cruncher_agent import JSONCruncher
from tests.fixtures.fixtures import valid_game_state


@patch.object(SceneGenerator, "new_scene")
def test_dispatch_command_generate_scene(mock_new_scene):
    # Create a sample game state
    state = valid_game_state

    # Test 1: generate_scene

    mock_new_scene.return_value = GameState(
        current_scene={
            "id": "mocked_scene_name",
            "description": "SceneGenerator.new_scene() was called.",
        },
        inventory=state.inventory,
        engine=state.engine,
        story=state.story,
        feedback=state.feedback,
    )

    # Create a sample dispatcher dictionary
    dispatcher_dict = {
        "command": "generate_scene",
        "parameters": "A library with a giant window, a spiral staircase, two other exits, and a secret map.",
    }

    # Call the dispatch function
    new_state = dispatch_command(dispatcher_dict, state)

    # Assert that the new state is updated correctly
    assert new_state.current_scene == {
        "id": "mocked_scene_name",
        "description": "SceneGenerator.new_scene() was called.",
    }
    assert new_state.inventory == state.inventory
    assert new_state.engine == state.engine
    assert new_state.story == state.story
    assert new_state.feedback == state.feedback


@patch.object(SceneGenerator, "update_scene")
def test_dispatch_command_update_scene(mock_update_scene):
    # Create a sample game state
    state = valid_game_state

    # Test 1: generate_scene

    mock_update_scene.return_value = GameState(
        current_scene={
            "id": "mocked_scene_name",
            "description": "SceneGenerator.update_scene() was called.",
        },
        inventory=state.inventory,
        engine=state.engine,
        story=state.story,
        feedback=state.feedback,
    )

    # Create a sample dispatcher dictionary
    dispatcher_dict = {
        "command": "update_scene",
        "parameters": "A library with a giant window, a spiral staircase, two other exits, and a secret map.",
    }

    # Call the dispatch function
    new_state = dispatch_command(dispatcher_dict, state)

    # Assert that the new state is updated correctly
    assert new_state.current_scene == {
        "id": "mocked_scene_name",
        "description": "SceneGenerator.update_scene() was called.",
    }
    assert new_state.inventory == state.inventory
    assert new_state.engine == state.engine
    assert new_state.story == state.story
    assert new_state.feedback == state.feedback


def test_dispatch_command_noop():
    # Create a sample game state
    state = valid_game_state

    # Create a sample dispatcher dictionary
    dispatcher_dict = {"command": "noop"}

    # Call the dispatch function
    new_state = dispatch_command(dispatcher_dict, state)

    # Assert that the new state is exactly the same as the old state
    assert new_state.current_scene == state.current_scene
    assert new_state.inventory == state.inventory
    assert new_state.engine == state.engine
    assert new_state.story == state.story
    assert new_state.feedback == state.feedback


def test_dispatch_command_feedback():
    # Create a sample game state
    state = valid_game_state

    # Create a sample dispatcher dictionary
    dispatcher_dict = {
        "command": "feedback",
        "parameters": "You move the rug and discover a trapdoor!",
    }

    # Call the dispatch function
    new_state = dispatch_command(dispatcher_dict, state)

    # Assert that the new state is updated correctly
    assert new_state.current_scene == state.current_scene
    assert new_state.inventory == state.inventory
    assert new_state.engine == state.engine
    assert new_state.story == state.story
    assert new_state.feedback == "You move the rug and discover a trapdoor!"


def test_dispatch_command_invalid_command():
    # Create a sample game state
    state = valid_game_state

    # Create a sample dispatcher dictionary
    dispatcher_dict = {"command": "invalid_command"}

    # Call the dispatch function
    with pytest.raises(ValueError):
        dispatch_command(dispatcher_dict, state)


@patch.object(JSONCruncher, "json_from_text")
def test_dispatch_command_restructure_scene(mock_json_from_text):
    # Create a sample game state
    state = valid_game_state

    # Create a sample dispatcher dictionary
    dispatcher_dict = {
        "command": "restructure_scene",
        "parameters": "A library with a giant window, a spiral staircase, two other exits, and a secret map.",
    }

    mock_json_from_text.return_value = {
        "id": "mocked_scene_name",
        "description": "JSONCruncher.json_from_text was called.",
    }

    # Call the dispatch function
    new_state = dispatch_command(dispatcher_dict, state)

    mock_json_from_text.assert_called_once_with(
        "A library with a giant window, a spiral staircase, two other exits, and a secret map.",
        "scene",
    )

    # Assert that the new state is updated correctly
    assert new_state.current_scene == {
        "id": "mocked_scene_name",
        "description": "JSONCruncher.json_from_text was called.",
    }
    assert new_state.inventory == state.inventory
    assert new_state.engine == state.engine
    assert new_state.story == state.story
    assert new_state.feedback == state.feedback


def test_extract_commands():
    # Create a sample game state
    state = valid_game_state

    # Test case 1: Single command
    text = "You can enter the room, sure. <GENERATE SCENE> A library with a giant window, a spiral staircase, two other exits, and a secret map."
    expected_commands = [
        {
            "command": "generate_scene",
            "parameters": "A library with a giant window, a spiral staircase, two other exits, and a secret map.",
            "last_scene": valid_game_state.current_scene,
        }
    ]
    result = extract_commands(text, state)
    assert result[0]["command"] == expected_commands[0]["command"]
    assert result[0]["parameters"] == expected_commands[0]["parameters"]
    assert result[0]["last_scene"] == expected_commands[0]["last_scene"]

    # # Test case 2: Multiple commands
    text = "<FEEDBACK> You move the rug and discover a trapdoor!\n <UPDATE SCENE> Make the trapdoor exit unhidden."
    expected_commands = [
        {
            "command": "feedback",
            "parameters": "You move the rug and discover a trapdoor!",
        },
        {
            "command": "update_scene",
            "parameters": "Make the trapdoor exit unhidden.",
            "scene": valid_game_state.current_scene,
        },
    ]
    result = extract_commands(text, state)
    assert result[0]["command"] == expected_commands[0]["command"]
    assert result[0]["parameters"] == expected_commands[0]["parameters"]
    assert result[0].get("last_scene") == None

    assert result[1]["command"] == expected_commands[1]["command"]
    assert result[1]["parameters"] == expected_commands[1]["parameters"]
    assert result[1]["scene"] == expected_commands[1]["scene"]

    assert len(result) == len(expected_commands)

    # # Test case 3: No commands
    text = "This is a plain text without any commands."
    expected_commands = []
    assert extract_commands(text, state) == expected_commands


@patch("lib.dispatcher.extract_commands")
@patch("lib.dispatcher.dispatch_command")
def test_dispatch_with_single_command(mock_dispatch_command, mock_extract_commands):
    # Create a sample game state
    state = valid_game_state

    mock_extract_commands.return_value = [
        {
            "command": "feedback",
            "parameters": "You can enter the room, sure.",
        }
    ]

    mock_dispatch_command.return_value = valid_game_state

    new_state = dispatch("<FEEDBACK>You can enter the room, sure.", state)

    mock_dispatch_command.assert_called_once_with(
        {
            "command": "feedback",
            "parameters": "You can enter the room, sure.",
        },
        state,
    )

    assert new_state == valid_game_state


@patch("lib.dispatcher.extract_commands")
@patch("lib.dispatcher.dispatch_command")
def test_dispatch_with_multiple_commands(mock_dispatch_command, mock_extract_commands):
    # Create a sample game state
    state = valid_game_state

    mock_updated_scene = state.current_scene.copy()
    mock_updated_scene["description"] = "There's a trapdoor under the rug."

    mock_extract_commands.return_value = [
        {
            "command": "feedback",
            "parameters": "You can enter the room, sure.",
        },
        {
            "command": "update_scene",
            "parameters": "Make the trapdoor exit unhidden.",
            "scene": valid_game_state.current_scene,
        },
    ]

    mock_dispatch_command.return_value = valid_game_state

    new_state = dispatch(
        "<FEEDBACK>You can enter the room, sure. <UPDATE SCENE> Make the trapdoor under the rug unhidden.",
        state,
    )

    assert mock_dispatch_command.call_args_list == [
        call(
            {
                "command": "feedback",
                "parameters": "You can enter the room, sure.",
            },
            state,
        ),
        call(
            {
                "command": "update_scene",
                "parameters": "Make the trapdoor exit unhidden.",
                "scene": valid_game_state.current_scene,
            },
            state,
        ),
    ]

    assert new_state == valid_game_state
