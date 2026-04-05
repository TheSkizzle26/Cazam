import sys
import platformdirs
import pyray as pr
import os
import setproctitle

from current_os import get_current_os, OSType
from config import Config
from system import SystemLinux, System
from core import Core
import cover
from palette import Palette
from gradient import Gradient
from bars import Bars


class Main:
    """
    The main program.
    """

    def __init__(self):
        setproctitle.setproctitle("cazam")

        self.config = Config()
        self.config_use_local_files = bool(self.config["use_local_cover_palette"])
        self.config_music_file_path = self.config["music_file_path"].removesuffix("/").removesuffix("\\")

        self.width, self.height = 1920, 1080
        self.width_ffi = pr.ffi.new("int *", self.width)
        self.height_ffi = pr.ffi.new("int *", self.height)
        self.init_window()

        match get_current_os():
            case OSType.Linux:
                print("Linux detected.")
                self.system = SystemLinux()
            case _:
                print("Couldn't detect OS or OS not fully supported.\nSome features won't work.")
                self.system = System()

        self.core = Core(self.config)
        self.palette = Palette(self.config)
        self.gradient = Gradient(self.config, self.palette)
        self.bars = Bars(self.config, self.core)

        self.gradient_texture_bg = pr.load_render_texture(self.width, self.height)
        self.gradient_texture_fg = pr.load_render_texture(self.width, self.height)
        self.bars_texture = pr.load_render_texture(self.width, self.height)

        self.current_song_name = None
        self.last_sync_time = -999

        self.calculate_palette()

    def quit(self):
        """
        Close all windows and processes.
        """

        self.core.stop()
        pr.close_window()
        sys.exit()

    def init_window(self):
        """
        Initialize the window.
        """

        pr.set_config_flags(
            pr.ConfigFlags.FLAG_FULLSCREEN_MODE |
            pr.ConfigFlags.FLAG_WINDOW_RESIZABLE
        )
        pr.init_window(self.width, self.height, "Cazam")
        pr.set_window_monitor(self.config["monitor"])

        if self.config["vsync"]:
            target_fps = pr.get_monitor_refresh_rate(self.config["monitor"])
        else:
            target_fps = self.config["target_fps"]

        pr.set_target_fps(target_fps)

    def regenerate_render_textures(self):
        """
        Unload previous and generate new render textures.
        """

        pr.unload_render_texture(self.gradient_texture_bg)
        pr.unload_render_texture(self.gradient_texture_fg)
        pr.unload_render_texture(self.bars_texture)

        self.gradient_texture_bg = pr.load_render_texture(self.width, self.height)
        self.gradient_texture_fg = pr.load_render_texture(self.width, self.height)
        self.bars_texture = pr.load_render_texture(self.width, self.height)

    def find_song_path(self, path: str, name: str):
        """
        Find a song's local file path based off its name.
        :param path: path to start search from
        :param name: the song's name
        :return:
        """

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
        """
        Calculate palette based off raw image data if provided.
        :param image_data: the image's raw data
        """

        if image_data:
            self.palette.from_image_data(image_data)

        pr.begin_texture_mode(self.gradient_texture_bg)
        self.gradient.render((self.width, self.height), is_foreground=False)
        pr.end_texture_mode()

        pr.begin_texture_mode(self.gradient_texture_fg)
        self.gradient.render((self.width, self.height), is_foreground=True)
        pr.end_texture_mode()

    def sync(self):
        """
        Sync with system information.
        Regenerates palette if necessary.
        """

        if not self.config_use_local_files:
            return

        self.system.fetch()
        song_name = self.system.get_song_name()

        if song_name != self.current_song_name:
            self.current_song_name = song_name
            song_path = self.system.get_song_path()

            if not song_path:
                print("Player doesn't provide song path, let's search for it...")

                if self.config_music_file_path:
                    path = self.config_music_file_path
                else:
                    path = platformdirs.user_music_dir()

                song_path = self.find_song_path(path, song_name)

            if song_path:
                print(f"Found song path. ({song_path})")
            else:
                print(f"Couldn't find song path ({song_name})")

            image_data = cover.extract_file_cover(song_path)
            self.calculate_palette(image_data)

    def adapt_window_size(self):
        """
        Change size of the internal render textures to the current window's size.
        """

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
        """
        Update everything.
        """

        now = pr.get_time()

        if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
            self.quit()

        self.adapt_window_size()

        if now - self.last_sync_time > 1:
            self.last_sync_time = now
            self.sync()

    def draw_render_texture(self, render_texture: pr.RenderTexture):
        """
        Draw a render texture at 0, 0.
        :param render_texture: the render texture to be drawn
        """

        pr.draw_texture_rec(
            render_texture.texture,
            (0, 0, self.width, -self.height),
            (0, 0),
            pr.WHITE
        )

    def render_bars(self):
        """
        Render all the bars in a fancy way.
        """

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
        """
        Render everything.
        """

        pr.begin_drawing()

        self.draw_render_texture(self.gradient_texture_bg)
        self.render_bars()

        pr.end_drawing()

    def run(self):
        """
        Run the main program and continuously call update and render functions.
        """

        while not pr.window_should_close():
            self.update()
            self.render()
            pr.set_window_title(f"FPS: {pr.get_fps()}")

        self.quit()


if __name__ == '__main__':
    Main().run()