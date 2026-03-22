import os
from .mp3 import extract_mp3_cover


def extract_file_cover(path: str):
    if not os.path.exists(path):
        return None

    if path.endswith(".mp3"):
        return extract_mp3_cover(path)

    return None