import pyray as pr

from config import Config
from core import Core


class Bars:
    def __init__(self, config: Config, core: Core):
        self.config = config
        self.core = core

        self.config_num_bars = self.config["num_bars"]
        self.config_bar_spacing = self.config["bar_spacing"]
        self.config_bar_height_percent = self.config["bar_height"]

    def render(self, screen_size: tuple[int, int]):
        width = screen_size[0] / self.config_num_bars
        max_height = (self.config_bar_height_percent / 100) * screen_size[1]

        for i in range(self.core.get_num_bars()):
            val = self.core.get_bar_value(i)
            height = val * max_height

            pr.draw_rectangle(
                int(i*width), int(screen_size[1] - height),
                int(width - self.config_bar_spacing), int(height),
                pr.WHITE
            )