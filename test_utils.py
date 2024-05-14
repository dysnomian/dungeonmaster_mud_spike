import sys

sys.path.append(".")

from utils import extract_from_fenced_code_block, extract_fenced_json

irl_example = """
"Here is the response:\n\n{\n  \"scene\": \"{\\\"id\\\": \\\"hallway\\\", \\\"title\\\": \\\"Hallway\\\", \\\"short_description\\\": \\\"You are in a long, dark hallway.\\\", \\\"long_description\\\": \\\"You are in a long, dark hallway with stone walls and a cold, grey floor. The air is musty and damp. Ahead of you, the hallway stretches out into darkness.\\\", \\\"number_of_visits\\\": 0, \\\"exits\\\": {\\\"north\\\": {\\\"short_description\\\": \\\"Door with metal bars\\\", \\\"locked\\\": true}, \\\"south\\\": {\\\"short_description\\\": \\\"Wall\\\"}}}\",\n  \"inventory\": []\n}\n\nThe player has successfully gone south and is now in the hallway. The door behind them was just a wooden door, but it's not going anywhere - they're stuck at this end of the hall for now."
"""


def test_extract_from_fenced_code_block():
    # Test case 1: Valid JSON code block
    text1 = 'Here is the JSON you asked for:\n\n```json\n{\n"scene":"A new scene"\n}\n```\n\nI hope this helps.'
    expected_output1 = '{\n"scene":"A new scene"\n}'
    assert extract_from_fenced_code_block(text1) == expected_output1

    # Test case 2: Valid code block without language specified
    text2 = 'Here is the JSON you asked for:\n\n```\n{\n"scene":"A new scene"\n}\n```\n\nI hope this helps.'
    expected_output2 = '{\n"scene":"A new scene"\n}'
    assert extract_from_fenced_code_block(text2) == expected_output2

    # Test case 3: Valid JSON code block with no surrounding text
    text3 = '```json\n{\n"scene":"A new scene"\n}\n```'
    expected_output3 = '{\n"scene":"A new scene"\n}'
    assert extract_from_fenced_code_block(text3) == expected_output3

    # Test case 4: Valid code block with no language specified and no surrounding text
    text4 = '```{\n"scene":"A new scene"\n}```'
    expected_output4 = '{\n"scene":"A new scene"\n}'
    assert extract_from_fenced_code_block(text4) == expected_output4

    # Test case 5: Invalid code block index
    text5 = 'Here is the JSON you asked for:\n\n```json\n{\n"scene":"A new scene"\n}\n```\n\nI hope this helps.'
    expected_output5 = None
    assert extract_from_fenced_code_block(text5, n=1) == expected_output5

    # Test case 6: No code blocks present
    text6 = "Here is some text without any code blocks."
    expected_output6 = None
    assert extract_from_fenced_code_block(text6) == expected_output6

    # Test case 7: Empty input text
    text7 = ""
    expected_output7 = None
    assert extract_from_fenced_code_block(text7) == expected_output7

    print("All test cases pass")


test_extract_from_fenced_code_block()


def test_extract_fenced_json():
    # Test case 1: Valid JSON code block
    text1 = 'Here is the JSON you asked for:\n\n```json\n{\n"scene":"A new scene"\n}\n```\n\nI hope this helps.'
    expected_output1 = {"scene": "A new scene"}
    assert extract_fenced_json(text1) == expected_output1

    # Test case 2: Valid code block without language specified
    text2 = 'Here is the JSON you asked for:\n\n```\n{\n"scene":"A new scene"\n}\n```\n\nI hope this helps.'
    expected_output2 = {"scene": "A new scene"}
    assert extract_fenced_json(text2) == expected_output2

    # Test case 3: Valid JSON code block with no surrounding text
    text3 = '```json\n{\n"scene":"A new scene"\n}\n```'
    expected_output3 = {"scene": "A new scene"}
    assert extract_fenced_json(text3) == expected_output3

    # Test case 4: Valid code block with no language specified and no surrounding text
    text4 = '```{\n"scene":"A new scene"\n}```'
    expected_output4 = {"scene": "A new scene"}
    assert extract_fenced_json(text4) == expected_output4

    # Test case 6: No code blocks present
    text6 = "Here is some text without any code blocks."
    expected_output6 = {}
    assert extract_fenced_json(text6) == expected_output6

    # Test case 7: Empty input text
    text7 = ""
    expected_output7 = {}
    assert extract_fenced_json(text7) == expected_output7

    # Test case 8: Text is a valid JSON object but not in a code block
    text8 = '{"scene":"A new scene"}'
    expected_output8 = {"scene": "A new scene"}
    assert extract_fenced_json(text8) == expected_output8

    print("All test cases pass")


test_extract_fenced_json()
