import os

from phgen.phsong import PowerHourSong

class PowerHourConfig:
    default_font_size: int = 72

    def __init__(self,
                 project_name: str,
                 fade_duration: float = 0.5,
                 text_padding: float = 100,
                 text_padding_x: float = -1,
                 text_padding_y: float = -1,
                 font_file: str = "Oswald.ttf",
                 font_color: str = "white",
                 font_size_scale: float = 1,
                 font_border_width: int = 5,
                 font_border_color: str = "black",
                 title_start_time: float = 0.5,
                 title_duration: float = 5,
                 name_duration: float = 5,
                 name_format: str = "Added by {name}",
                 interstitial_text: str = "Drink!",
                 target_res: str = "1080p"):
        self.project_name = project_name
        self.fade_duration = fade_duration
        self.text_padding_x = text_padding_x if text_padding_x >= 0 else text_padding
        self.text_padding_y = text_padding_y if text_padding_y >= 0 else text_padding
        self.font_color = font_color
        scaled_font_size = self.default_font_size * font_size_scale
        self.title_font_size = scaled_font_size
        self.artist_font_size = scaled_font_size * 0.5
        self.number_font_size = scaled_font_size * 3
        self.interstitial_font_size = scaled_font_size * 2
        self.font_border_width = font_border_width
        self.font_border_color = font_border_color
        self.title_start_time = title_start_time
        self.title_duration = title_duration
        self.name_duration = name_duration
        self.name_format = name_format
        self.font_file = font_file
        self.interstitial_text = interstitial_text
        self.target_res = target_res

    def get_ph_filename(self, num: int, song: PowerHourSong, ext: str = "mp4") -> str:
        return f"song.{song.get_filename(ext)}"

    def get_full_font_path(self):
        return os.path.join(os.getcwd(), self.font_file)

    def get_dir_path(self):
        dir_path = os.getcwd()
        if self.project_name == "":
            return dir_path
        dir_path = os.path.join(dir_path, self.project_name)
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        return dir_path
