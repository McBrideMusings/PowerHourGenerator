from enum import Enum


class PowerHourConfig:
    default_font_size: int = 64

    def __init__(self,
                 project_name: str,
                 fade_duration: float = 0.5,
                 text_padding: float = 100,
                 text_padding_x: float = -1,
                 text_padding_y: float = -1,
                 font_file: str = "",
                 font_color: str = "white",
                 font_size_scale: float = 1,
                 font_border_width: int = 5,
                 font_border_color: str = "black",
                 title_start_time: float = 0.5,
                 title_duration: float = 5,
                 interstitial_text: str = "Drink!"):
        self.project_name = project_name
        self.fade_duration = fade_duration
        self.text_padding_x = text_padding_x if text_padding_x >= 0 else text_padding
        self.text_padding_y = text_padding_y if text_padding_y >= 0 else text_padding
        self.font_color = font_color
        scaled_font_size = self.default_font_size * font_size_scale
        self.title_font_size = scaled_font_size
        self.artist_font_size = scaled_font_size * 0.8
        self.number_font_size = scaled_font_size * 4
        self.interstitial_font_size = scaled_font_size * 2
        self.font_border_width = font_border_width
        self.font_border_color = font_border_color
        self.title_start_time = title_start_time
        self.title_duration = title_duration
        self.font_file = font_file
        self.interstitial_text = interstitial_text


class PowerHourSong:
    def __init__(self, title: str, artist: str, start_time: int, link: str):
        self.title = title
        self.artist = artist
        self.start_time = start_time
        self.link = link
        self.end_time = start_time + 60
        self.title_start_time = start_time + 0.5
        self.title_end_time = self.title_start_time + 5

    def __str__(self):
        return "SongChoice({}, {}, {}, {})".format(self.title, self.artist, self.start_time, self.link)

    def get_filename(self, file_ending: str = "mp4", *extras: str):
        filename = f"{self.title.replace(' ', '')}.{self.artist.replace(' ', '')}"
        if len(extras) > 0:
            for extra in extras:
                filename = f"{filename}.{extra}"
        return filename + f".{file_ending}"



