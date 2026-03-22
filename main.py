import sys
import pyray as pr
import os

from config import Config
from system import SystemLinux
from core import Core
from palette import Palette
from gradient import Gradient
from bars import Bars


class Main:
    def __init__(self):
        self.width, self.height = 1920, 1080
        pr.set_config_flags(
            pr.ConfigFlags.FLAG_FULLSCREEN_MODE
        )
        pr.init_window(self.width, self.height, "Cazam")
        pr.set_window_monitor(0)

        self.config = Config()
        self.system = SystemLinux()
        self.core = Core(144)
        self.palette = Palette()
        self.gradient = Gradient(self.config, self.palette, (self.width, self.height))
        self.bars = Bars(self.config, self.core)

        self.gradient_texture = pr.load_render_texture(self.width, self.height)
        self.calculate_palette()

    def find_song_path(self, path: str, name: str):
        for sub_dir in os.listdir(path):
            full_path = f"{path}/{sub_dir}"

            if os.path.isdir(full_path):
                ret = self.find_song_path(full_path, name)
                if len(ret): return ret
            elif sub_dir.endswith((".mp3", ".wav", ".ogg", ".flac")):
                if sub_dir.startswith(name):
                    return full_path

        return ""

    def calculate_palette(self, image_data=None):
        if image_data:
            self.palette.from_image_data(image_data)

        pr.begin_texture_mode(self.gradient_texture)
        self.gradient.render((self.width, self.height))
        pr.end_texture_mode()

    def sync(self):
        ...

    def update(self):
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
            pr.close_window()
            sys.exit()

        self.core.fetch() # handles fps for some reason

    def render(self):
        pr.begin_drawing()
        pr.clear_background(pr.BLACK)

        pr.draw_texture_rec(
            self.gradient_texture.texture,
            (0, 0, self.width, -self.height),
            (0, 0),
            pr.WHITE
        )

        self.bars.render((self.width, self.height))

        pr.end_drawing()

    def run(self):
        while True:
            self.update()
            self.render()

            pr.set_window_title(f"FPS: {pr.get_fps()}")


if __name__ == '__main__':
    Main().run()