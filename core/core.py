import struct
import subprocess
import tempfile
import threading
import pyray as pr

from config import Config


class Core:
    def __init__(self, config: Config):
        self.config_pattern = """
[general]
autosens = 1
bars = %d
framerate = %d
[output]
method = raw
raw_target = %s
bit_format = %s
"""
        self.num_bars = config["num_bars"]
        self.target_fps = 144
        self.out_bit_format = "16bit"
        self.raw_target = "/dev/stdout"

        self.config = self.config_pattern % (self.num_bars, self.target_fps, self.raw_target, self.out_bit_format)
        self.byte_type, self.byte_size, self.byte_norm = ("H", 2, 65535) if self.out_bit_format == "16bit" else ("B", 1, 255)

        self.config_file = tempfile.NamedTemporaryFile("w")
        self.config_file.write(self.config)
        self.config_file.flush()

        self.process = subprocess.Popen(["cava", "-p", self.config_file.name], stdout=subprocess.PIPE)
        self.chunk_size = self.byte_size * self.num_bars
        self.format = self.byte_type * self.num_bars
        self.source = self.process.stdout # change for different raw_target

        self.bar_values = [0] * self.num_bars
        self.last_bar_values = [0] * self.num_bars
        self.last_fetch_time = 0

        self.stop_thread = False
        self.thread = threading.Thread(target=self.fetch_thread)
        self.thread.start()

    def fetch_thread(self):
        while not self.stop_thread:
            data = self.source.read(self.chunk_size)
            if len(data) < self.chunk_size:
                return

            self.last_bar_values = self.bar_values
            self.bar_values = [i / self.byte_norm for i in struct.unpack(self.format, data)]
            self.last_fetch_time = pr.get_time()

    def stop(self):
        self.stop_thread = True

    def get_num_bars(self):
        return self.num_bars

    def get_bar_value(self, idx: int) -> float:
        if idx >= self.num_bars:
            return 0

        now = pr.get_time()
        t = (now - self.last_fetch_time) / (1 / self.target_fps)

        last = self.last_bar_values[idx]
        cur = self.bar_values[idx]

        return last + t*(cur - last)