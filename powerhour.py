class PowerHourSong:
    def __init__(self, title: str, artist: str, start_time: int, link: str):
        self.title = title
        self.artist = artist
        self.start_time = start_time
        self.link = link

    def __str__(self):
        return "SongChoice({}, {}, {}, {})".format(self.title, self.artist, self.start_time, self.link)

    def get_filename(self, file_ending: str = "mp4"):
        return "{}.{}.{}".format(self.title.replace(' ', ''), self.artist.replace(' ', ''),file_ending)


class PowerHourConfig:
    def __init__(self, output_path: str, fade_duration: int = 0.5):
        self.output_path = output_path
        self.fade_duration = fade_duration
