import sys
import platformdirs
import pyray as pr
import os

from config import Config
from system import SystemLinux
from core import Core
import cover
from palette import Palette
from gradient import Gradient
from bars import Bars


class Main:
    def __init__(self):
        self.config = Config()
        self.config_monitor = self.config["monitor"]
        self.config_use_vsync = bool(self.config["vsync"])
        self.config_target_fps = bool(self.config["target_fps"])
        self.config_use_local_files = bool(self.config["use_local_cover_palette"])
        self.target_fps = -1 # set by init_window

        self.width, self.height = 1920, 1080
        self.width_ffi = pr.ffi.new("int *", self.width)
        self.height_ffi = pr.ffi.new("int *", self.height)
        self.init_window()

        self.system = SystemLinux()
        self.core = Core(self.config, self.target_fps)
        self.palette = Palette(self.config)
        self.gradient = Gradient(self.config, self.palette)
        self.bars = Bars(self.config, self.core)

        self.gradient_texture_bg = pr.load_render_texture(self.width, self.height)
        self.gradient_texture_fg = pr.load_render_texture(self.width, self.height)
        self.bars_texture = pr.load_render_texture(self.width, self.height)

        self.current_song_name = None
        self.last_sync_time = -999

        self.calculate_palette()

    def init_window(self):
        if self.config_use_vsync:
            self.target_fps = pr.get_monitor_refresh_rate(self.config_monitor)
        else:
            self.target_fps = self.config_target_fps

        pr.set_config_flags(
            pr.ConfigFlags.FLAG_FULLSCREEN_MODE |
            pr.ConfigFlags.FLAG_WINDOW_RESIZABLE
        )
        pr.init_window(self.width, self.height, "Cazam")
        pr.set_window_monitor(self.config_monitor)

    def regenerate_render_textures(self):
        if self.gradient_texture_bg: pr.unload_render_texture(self.gradient_texture_bg)
        if self.gradient_texture_fg: pr.unload_render_texture(self.gradient_texture_fg)
        if self.bars_texture: pr.unload_render_texture(self.bars_texture)

        self.gradient_texture_bg = pr.load_render_texture(self.width, self.height)
        self.gradient_texture_fg = pr.load_render_texture(self.width, self.height)
        self.bars_texture = pr.load_render_texture(self.width, self.height)

    def find_song_path(self, path: str, name: str):
        for sub_dir in os.listdir(path):
            full_path = f"{path}/{sub_dir}"

            if os.path.isdir(full_path):
                ret = self.find_song_path(full_path, name)
                if ret: return ret
            elif sub_dir.endswith((".mp3", ".wav", ".ogg", ".flac")):
                if sub_dir.startswith(name):
                    return full_path

        return ""

    def calculate_palette(self, image_data=None):
        if image_data:
            self.palette.from_image_data(image_data)

        pr.begin_texture_mode(self.gradient_texture_bg)
        self.gradient.render((self.width, self.height), is_foreground=False)
        pr.end_texture_mode()

        pr.begin_texture_mode(self.gradient_texture_fg)
        self.gradient.render((self.width, self.height), is_foreground=True)
        pr.end_texture_mode()

    def sync(self):
        if not self.config_use_local_files:
            return

        self.system.fetch()
        song_name = self.system.get_song_name()

        if song_name != self.current_song_name:
            self.current_song_name = song_name
            song_path = self.system.get_song_path()

            if not song_path:
                # not provided by player
                song_path = self.find_song_path(platformdirs.user_music_dir(), song_name)

            image_data = cover.extract_file_cover(song_path)
            self.calculate_palette(image_data)

    def adapt_window_size(self):
        pr.glfw_get_window_size(pr.get_window_handle(), self.width_ffi, self.height_ffi)
        window_size = (
            self.width_ffi[0],
            self.height_ffi[0],
        )

        if window_size != (self.width, self.height):
            self.width = window_size[0]
            self.height = window_size[1]

            self.regenerate_render_textures()
            self.calculate_palette()

    def update(self):
        now = pr.get_time()

        if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
            pr.close_window()
            sys.exit()

        self.adapt_window_size()

        if now - self.last_sync_time > 1:
            self.last_sync_time = now
            self.sync()

        self.core.fetch() # handles fps for some reason

    def draw_render_texture(self, render_texture: pr.RenderTexture):
        pr.draw_texture_rec(
            render_texture.texture,
            (0, 0, self.width, -self.height),
            (0, 0),
            pr.WHITE
        )

    def render_bars(self):
        pr.begin_texture_mode(self.bars_texture)
        pr.clear_background(pr.BLANK)
        self.bars.render((self.width, self.height))
        pr.end_texture_mode()

        pr.begin_texture_mode(self.bars_texture)
        pr.begin_blend_mode(pr.BlendMode.BLEND_MULTIPLIED)
        pr.draw_texture_rec(
            self.gradient_texture_fg.texture,
            (0, 0, self.width, -self.height),
            (0, 0),
            pr.WHITE
        )
        pr.end_blend_mode()
        pr.end_texture_mode()

        self.draw_render_texture(self.bars_texture)

    def render(self):
        pr.begin_drawing()

        self.draw_render_texture(self.gradient_texture_bg)
        self.render_bars()

        pr.end_drawing()

    def run(self):
        while True:
            self.update()
            self.render()

            pr.set_window_title(f"FPS: {pr.get_fps()}")


if __name__ == '__main__':
    Main().run()