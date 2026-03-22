import pyray as pr

from config import Config
from palette import Palette


class Gradient:
    def __init__(self, config: Config, palette: Palette):
        self.config = config
        self.palette = palette
        self.num_colors = 3

        self.shader = pr.load_shader("", "shaders/gradient.frag")
        self.upload_colors()

        # fix shader rect bug using this (don't ask me how)
        texture = pr.Texture(
            pr.rl_get_texture_id_default(),
            1, 1,
            1,
            pr.PixelFormat.PIXELFORMAT_UNCOMPRESSED_R8G8B8A8
        )
        pr.set_shapes_texture(
            texture,
            (0, 0, 1, 1)
        )

    def set_uniform(self, name: str, value, cdecl: str, uniform_type: int):
        value = pr.ffi.new(cdecl, value)
        pr.set_shader_value(
            self.shader,
            pr.get_shader_location(self.shader, name),
            value,
            uniform_type
        )

    def upload_colors(self, is_foreground=False):
        colors = []
        for i in range(self.num_colors):
            [colors.append(v) for v in self.palette.get_color_float(i + int(is_foreground*self.num_colors))]

        value = pr.ffi.new("float[]", colors)
        pr.set_shader_value_v(
            self.shader,
            pr.get_shader_location(self.shader, "colors"),
            value,
            pr.ShaderUniformDataType.SHADER_UNIFORM_VEC3,
            len(colors)
        )

    def render(self, screen_size: tuple[int, int], is_foreground=False):
        pr.begin_shader_mode(self.shader)

        self.upload_colors(is_foreground)

        # screen_width
        self.set_uniform(
            "screenWidth",
            screen_size[0],
            "int*",
            pr.ShaderUniformDataType.SHADER_UNIFORM_INT
        )

        # aspect ratio
        self.set_uniform(
            "aspectRatio",
            screen_size[0] / screen_size[1],
            "float*",
            pr.ShaderUniformDataType.SHADER_UNIFORM_FLOAT
        )

        # noise amount
        self.set_uniform(
            "noiseAmount",
            self.config[f"{"fg" if is_foreground else "bg"}_noise_amount"],
            "float*",
            pr.ShaderUniformDataType.SHADER_UNIFORM_FLOAT
        )

        pr.draw_rectangle(
            0, 0,
            *screen_size,
            pr.WHITE
        )

        pr.end_shader_mode()