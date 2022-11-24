from enum import Enum


class PowerHourConfig:
    default_font_size: int = 64

    def __init__(self, output_path: str, fade_duration: float = 0.5, text_padding: float = 100,
                 text_padding_x: float = -1, text_padding_y: float = -1, font_file: str = "",
                 font_color: str = "white", font_size_scale: float = 1, font_border_width: int = 5,
                 font_border_color: str = "black", title_start_time: float = 0.5, title_duration: float = 5):
        self.output_path = output_path
        self.fade_duration = fade_duration
        self.text_padding_x = text_padding_x if text_padding_x >= 0 else text_padding
        self.text_padding_y = text_padding_y if text_padding_y >= 0 else text_padding
        self.font_color = font_color
        scaled_font_size = self.default_font_size * font_size_scale
        self.title_font_size = scaled_font_size
        self.artist_font_size = scaled_font_size * 0.8
        self.number_font_size = scaled_font_size * 4
        self.font_border_width = font_border_width
        self.font_border_color = font_border_color
        self.title_start_time = title_start_time
        self.title_duration = title_duration
        self.font_file = font_file


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

    def get_filename(self, file_ending: str = "mp4"):
        return "{}.{}.{}".format(self.title.replace(' ', ''), self.artist.replace(' ', ''), file_ending)


class PosAnchor(Enum):
    CENTER = 1
    TOP_LEFT = 2
    TOP_CENTER = 3
    TOP_RIGHT = 4
    BOTTOM_LEFT = 5
    BOTTOM_CENTER = 6
    BOTTOM_RIGHT = 7


class VideoPos:
    """A two-dimensional vector with Cartesian coordinates."""

    # Padding doesn't apply to centered
    center_x: str = '(w-text_w)/2'
    center_y: str = '(h-text_h)/2'

    top_left_x_fmt: str = '{padding}'
    top_left_y_fmt: str = '{padding}'
    top_center_x: str = '(w-text_w)/2'
    top_center_y_fmt: str = '{padding}'
    top_right_x_fmt: str = 'w-tw-{padding}'
    top_right_y_fmt: str = '{padding}'

    bottom_left_x_fmt: str = '{padding}'
    bottom_left_y_fmt: str = 'h-th-{padding}'
    bottom_center_x: str = '(w-text_w)/2'
    bottom_center_y_fmt: str = 'h-th-{padding}'
    bottom_right_x_fmt: str = 'w-tw-{padding}'
    bottom_right_y_fmt: str = 'h-th-{padding}'

    def __init__(self, anchor: PosAnchor, padding: float):
        self.anchor = anchor
        self.padding = padding

    def __str__(self):
        """Human-readable string representation of the vector."""
        return 'x={} y={}'.format(self.get_x_expr(), self.get_x_expr())

    def get_x_expr(self, offset: float = 0):
        match self.anchor:
            case PosAnchor.CENTER:
                return self.center_x
            case PosAnchor.TOP_LEFT:
                return self.top_left_x_fmt.format(padding=self.padding + offset)
            case PosAnchor.TOP_CENTER:
                return self.top_center_x
            case PosAnchor.TOP_RIGHT:
                return self.top_right_x_fmt.format(padding=self.padding + offset)
            case PosAnchor.BOTTOM_LEFT:
                return self.bottom_left_x_fmt.format(padding=self.padding + offset)
            case PosAnchor.BOTTOM_CENTER:
                return self.bottom_center_x
            case PosAnchor.BOTTOM_RIGHT:
                return self.bottom_right_x_fmt.format(padding=self.padding + offset)

    def get_y_expr(self, offset: float = 0):
        match self.anchor:
            case PosAnchor.CENTER:
                return self.center_y
            case PosAnchor.TOP_LEFT:
                return self.top_left_y_fmt.format(padding=self.padding + offset)
            case PosAnchor.TOP_CENTER:
                return self.top_center_y_fmt.format(padding=self.padding + offset)
            case PosAnchor.TOP_RIGHT:
                return self.top_right_y_fmt.format(padding=self.padding + offset)
            case PosAnchor.BOTTOM_LEFT:
                return self.bottom_left_y_fmt.format(padding=self.padding + offset)
            case PosAnchor.BOTTOM_CENTER:
                return self.bottom_center_y_fmt.format(padding=self.padding + offset)
            case PosAnchor.BOTTOM_RIGHT:
                return self.bottom_right_y_fmt.format(padding=self.padding + offset)
