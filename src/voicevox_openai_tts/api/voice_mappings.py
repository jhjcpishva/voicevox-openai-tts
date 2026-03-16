from functools import lru_cache
import json
import os

DEFAULT_MAPPING_PATH = "/app/voice_mappings.json"


def get_voice_mappings_path() -> str:
    return os.getenv("VOICE_MAPPINGS_PATH", DEFAULT_MAPPING_PATH)


@lru_cache
def load_voice_mappings() -> dict[str, str]:
    """音声IDマッピングを読み込む"""
    try:
        with open(get_voice_mappings_path()) as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load voice mappings: {e}")
        return {}
