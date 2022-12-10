def clean_string(text: str):
    text = text.replace(' ', '')
    text = text.replace('?', '')
    text = text.replace(',', '')
    return text


class PowerHourSong:
    def __init__(self, title: str, artist: str, start_time: int, link: str,
                 duration: int = 60):
        self.title = title
        self.artist = artist
        self.start_time = start_time
        self.link = link
        duration = max(3, duration) # at least 3 sec other wtf is the user even doing
        self.end_time = start_time + duration
        self.title_start_time = start_time + 0.5
        self.title_end_time = self.title_start_time + 5

    def __str__(self):
        return f"SongChoice({self.title}, {self.artist}, {self.start_time}, {self.end_time}, {self.link})"

    def get_filename(self, file_ending: str = "mp4", *extras: str):
        title = clean_string(self.title)
        artist = clean_string(self.artist)
        filename = f"{title}.{artist}"
        if len(extras) > 0:
            for extra in extras:
                filename = f"{filename}.{extra}"
        return filename + f".{file_ending}"
