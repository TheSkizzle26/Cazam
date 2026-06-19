import eyed3 as ed


def extract_mp3_cover(path: str):
    """
    Extract an mp3's cover image.
    :param path: the path to the mp3 file
    :return: the raw image data
    """

    file = ed.load(path)

    for image in file.tag.images:
        return image.image_data # first one

    return None