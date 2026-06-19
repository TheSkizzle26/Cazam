import os
from .mp3 import extract_mp3_cover


def extract_file_cover(path: str):
    """
    Extract a file's cover image.
    :param path: the path to the file
    :return the raw image data
    """

    if not os.path.exists(path):
        return None

    if path.endswith(".mp3"):
        return extract_mp3_cover(path)

    return None