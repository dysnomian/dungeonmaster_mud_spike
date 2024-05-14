"Text-to-speech module"

import os
import subprocess

from sys import platform
from pathlib import Path

from openai import OpenAI


# For text to speech, I'm currently using Whisper. Probably want to swap this to Tortoise soon.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TTS_CLIENT = OpenAI(api_key=OPENAI_API_KEY)


def play_mp3(file_path: str) -> bool:
    "Platform-specific method to play an mp3 file."
    try:
        if platform == "darwin":
            subprocess.run(["afplay", file_path], check=True)
        elif platform == "win32":
            subprocess.run(["start", file_path], shell=True, check=True)
        elif platform == "linux":
            subprocess.run(["ffplay", file_path], check=True)
        else:
            print("Unsupported platform for text to speech.")
        return True
    except Exception as e:
        print(f"Error playing mp3: {e}")
        return False


def speak_text(text: str):
    "Speak the given text using AI text-to-speech."
    file_path = Path("tmp/speech.mp3")
    try:
        with TTS_CLIENT.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text,
        ) as response:
            response.stream_to_file(file_path)
            play_mp3(str(file_path))
            return True
    except Exception as e:
        print(f"Error speaking text: {e}")
        return False
