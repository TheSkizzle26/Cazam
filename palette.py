from PIL import Image
from io import BytesIO
from materialyoucolor.quantize import QuantizeCelebi
from materialyoucolor.score.score import Score
from materialyoucolor.scheme.scheme_tonal_spot import SchemeTonalSpot
from materialyoucolor.hct import Hct


class Palette:
    def __init__(self):
        self.colors = [(56, 30, 60), (107, 89, 108), (200, 138, 151)]
        self.text_color_light = (255, 239, 252)
        self.text_color_dark = (209, 173, 212)

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

        add = 0
        mul = 8

        tones = [2, 5, 8]
        for i in range(len(tones)):
            tones[i] = int(add + tones[i] * mul)

        self.colors = (
            self.argb_to_rgb(scheme.primary_palette.tone(tones[0])),
            self.argb_to_rgb(scheme.secondary_palette.tone(tones[1])),
            self.argb_to_rgb(scheme.tertiary_palette.tone(tones[2])),
        )

        self.text_color_light = self.argb_to_rgb(scheme.primary_palette.tone(96))
        self.text_color_dark = self.argb_to_rgb(scheme.primary_palette.tone(75))

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