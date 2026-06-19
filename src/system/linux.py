from dbus_next.aio import MessageBus
import asyncio

from .system import System


class SystemLinux(System):
    def __init__(self):
        self.is_playing = False
        self.song_path = ""
        self.song_title = ""
        self.song_album = ""
        self.song_artists = []
        self.song_length = 0
        self.song_position = 0

    async def fetch_async(self):
        bus = await MessageBus().connect()

        introspection = await bus.introspect("org.freedesktop.DBus", "/org/freedesktop/DBus")
        obj = bus.get_proxy_object("org.freedesktop.DBus", "/org/freedesktop/DBus", introspection)
        interface = obj.get_interface("org.freedesktop.DBus")

        names = await interface.call_list_names()

        players = [name for name in names if name.startswith("org.mpris.MediaPlayer2.") and not name.count("firefox")]

        if len(players) == 0:
            print("No players running!")
            self.is_playing = False
            return

        self.is_playing = True
        player = players[0]

        introspection = await bus.introspect(player, "/org/mpris/MediaPlayer2")
        obj = bus.get_proxy_object(player, "/org/mpris/MediaPlayer2", introspection)
        props = obj.get_interface("org.freedesktop.DBus.Properties")

        metadata = await props.call_get("org.mpris.MediaPlayer2.Player", "Metadata")

        path = metadata.value.get("xesam:location", None)
        title = metadata.value.get("xesam:title", None)
        album = metadata.value.get("xesam:album", None)
        artists = metadata.value.get("xesam:artist", None)
        length = metadata.value.get("mpris:length", None)

        if path: self.song_path = path.value
        if title: self.song_title = title.value
        if album: self.song_album = album.value
        if artists: self.song_artists = artists.value
        if length: self.song_length = length.value / 1_000_000

        if not (title and artists and length):
            print("Couldn't load data.")

        position = await props.call_get("org.mpris.MediaPlayer2.Player", "Position")
        self.song_position = position.value / 1_000_000

    def fetch(self):
        asyncio.run(self.fetch_async())

    def is_song_playing(self) -> bool:
        return self.is_playing

    def get_song_path(self) -> str:
        return self.song_path

    def get_song_name(self) -> str:
        return self.song_title

    def get_song_album(self) -> str:
        return self.song_album

    def get_song_artists(self) -> list[str]:
        return self.song_artists

    def get_song_length(self) -> float:
        return self.song_length

    def get_song_pos(self) -> float:
        return self.song_position