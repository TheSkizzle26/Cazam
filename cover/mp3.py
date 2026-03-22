import eyed3 as ed


def extract_mp3_cover(path: str):
    file = ed.load(path)

    for image in file.tag.images:
        return image.image_data # first one

    return None