from PIL import Image
from io import BytesIO
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.hct import Hct

from config import Config


class Palette:
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
    def argb_to_rgb(argb):
        r = (argb >> 16) & 0xFF
        g = (argb >> 8) & 0xFF
        b = argb & 0xFF
        return (
            r,
            g,
            b
        )

    def from_image_data(self, data: bytes):
        image = Image.open(BytesIO(data))
        pixels = list(image.getdata())

        if type(pixels[0]) == int:
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

        print(self.colors)

    def get_color(self, idx: int):
        if idx >= len(self.colors):
            return 0, 0, 0

        return self.colors[idx]

    def get_color_float(self, idx: int):
        color = self.get_color(idx)
        return (
            color[0] / 255,
            color[1] / 255,
            color[2] / 255,
        )

    def get_text_color_light(self):
        return self.text_color_light

    def get_text_color_dark(self):
        return self.text_color_dark