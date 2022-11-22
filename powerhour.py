from enum import Enum


class PowerHourSong:
    def __init__(self, title: str, artist: str, start_time: int, link: str):
        self.title = title
        self.artist = artist
        self.start_time = start_time
        self.link = link

    def __str__(self):
        return "SongChoice({}, {}, {}, {})".format(self.title, self.artist, self.start_time, self.link)

    def get_filename(self, file_ending: str = "mp4"):
        return "{}.{}.{}".format(self.title.replace(' ', ''), self.artist.replace(' ', ''), file_ending)


class PowerHourConfig:
    def __init__(self, output_path: str, fade_duration: int = 0.5):
        self.output_path = output_path
        self.fade_duration = fade_duration


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

    top_left_x_fmt : str = '{padding}'
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
        return '{:g}i + {:g}j'.format(self.x, self.y)

    def get_x_expr(self):
        match self.anchor:
            case PosAnchor.CENTER:
                return "Bad request"
            case 404:
                return "Not found"
            case 418:
                return "I'm a teapot"

    def get_y_expr(self):
        match self.anchor:
            case CENTER:
                return "Bad request"
            case 404:
                return "Not found"
            case 418:
                return "I'm a teapot"
