from PIL import Image
from io import BytesIO
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.hct import Hct

from config import Config


class Palette:
    """
    Generates and stores the palette to be used.
    """

    def __init__(self, config: Config):
        self.colors = [
            config["bg_color1"],
            config["bg_color2"],
            config["bg_color3"],
            config["fg_color1"],
            config["fg_color2"],
            config["fg_color3"],
        ]

    @staticmethod
    def argb_to_rgb(argb) -> tuple[int, int, int]:
        """
        Converts an ARGB integer to an RGB one.
        :param argb: ARGB color as a single integer
        :return: RGB color as a tuple with each value between 0 and 255
        """

        r = (argb >> 16) & 0xFF
        g = (argb >> 8) & 0xFF
        b = argb & 0xFF
        return (
            r,
            g,
            b
        )

    def from_image_data(self, data: bytes):
        """
        Auto-generate palette based off raw image data.
        :param data: the image's raw data
        """

        image = Image.open(BytesIO(data))
        pixels = list(image.getdata())

        if type(pixels[0]) == int: # invalid data
            pixels = [(0, 0, 0)]

        result = QuantizeCelebi(pixels, 128)

        colors = Score.score(result)

        seed = colors[0]
        scheme = SchemeTonalSpot(
            Hct.from_int(seed),
            True,
            0.0
        )

        tones_bg = [16, 40, 64]
        tones_fg = [64, 80, 96]

        self.colors = (
            self.argb_to_rgb(scheme.primary_palette.tone(tones_bg[0])), # foreground
            self.argb_to_rgb(scheme.secondary_palette.tone(tones_bg[1])),
            self.argb_to_rgb(scheme.tertiary_palette.tone(tones_bg[2])),
            self.argb_to_rgb(scheme.primary_palette.tone(tones_fg[0])), # background
            self.argb_to_rgb(scheme.secondary_palette.tone(tones_fg[1])),
            self.argb_to_rgb(scheme.tertiary_palette.tone(tones_fg[2])),
        )

    def get_color(self, idx: int) -> tuple[int, int, int]:
        """
        Get palette color at index.
        :param idx: the color's index
        :return: the RGB color as an integer tuple
        """

        if idx >= len(self.colors):
            return 0, 0, 0

        return self.colors[idx]

    def get_color_float(self, idx: int) -> tuple[float, float, float]:
        """
        Get palette color at index as a float tuple.
        :param idx: the color's index
        :return: the RGB color as a tuple with each value between 0 and 1
        """

        color = self.get_color(idx)
        return (
            color[0] / 255,
            color[1] / 255,
            color[2] / 255,
        )