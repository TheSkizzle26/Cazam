import sys
import pyray as pr

from core import Core


class Main:
    def __init__(self):
        self.width, self.height = 1920, 1080
        pr.set_config_flags(
            pr.ConfigFlags.FLAG_FULLSCREEN_MODE
        )
        pr.init_window(self.width, self.height, "Cazam")
        pr.set_window_monitor(0)

        self.core = Core(144)

    def update(self):
        if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
            pr.close_window()
            sys.exit()

        self.core.fetch() # handles fps for some reason

    def render(self):
        pr.begin_drawing()
        pr.clear_background(pr.BLACK)

        width = self.width // self.core.get_num_bars()

        for i in range(self.core.get_num_bars()):
            val = self.core.get_bar_value(i)
            height = int(val * self.height * 0.5)

            pr.draw_rectangle(
                i*width, self.height-height,
                width, height,
                pr.WHITE
            )

        pr.end_drawing()

    def run(self):
        while True:
            self.update()
            self.render()

            pr.set_window_title(f"FPS: {pr.get_fps()}")


if __name__ == '__main__':
    Main().run()