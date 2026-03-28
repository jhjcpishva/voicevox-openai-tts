from functools import lru_cache
import json

from ..settings import get_settings


def get_voice_mappings_path() -> str:
    return get_settings().voice_mappings_path


@lru_cache
def load_voice_mappings() -> dict[str, str]:
    """音声IDマッピングを読み込む"""
    try:
        with open(get_voice_mappings_path()) as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load voice mappings: {e}")
        return {}
