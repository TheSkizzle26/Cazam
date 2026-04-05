class System:
    """
    Handles fetching of all system-specific information.
    """

    def fetch(self):
        """
        Fetches all the system information.
        """
        ...

    def is_song_playing(self) -> bool:
        """
        :return: is a song currently playing?
        """
        ...

    def get_song_path(self) -> str:
        """
        :return: current song's local file path, empty if not provided
        """
        ...

    def get_song_name(self) -> str:
        """
        :return: the current song's name/title
        """
        ...

    def get_song_album(self) -> str:
        """
        :return: the current song's album name
        """
        ...

    def get_song_artists(self) -> list[str]:
        """
        :return: a list containing the names of the song's artists
        """
        ...

    def get_song_length(self) -> float:
        """
        :return: the current song's total length in seconds
        """
        ...

    def get_song_pos(self) -> float:
        """
        :return: get the current position the player is at inside the song, in seconds
        """
        ...