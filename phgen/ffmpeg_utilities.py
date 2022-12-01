from enum import Enum


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
                return self.center_x if offset == 0 else f"{self.center_x} + {offset}"
            case PosAnchor.TOP_LEFT:
                return self.top_left_x_fmt.format(padding=self.padding + offset)
            case PosAnchor.TOP_CENTER:
                return self.top_center_x if offset == 0 else f"{self.top_center_x} + {offset}"
            case PosAnchor.TOP_RIGHT:
                return self.top_right_x_fmt.format(padding=self.padding + offset)
            case PosAnchor.BOTTOM_LEFT:
                return self.bottom_left_x_fmt.format(padding=self.padding + offset)
            case PosAnchor.BOTTOM_CENTER:
                return self.bottom_center_x if offset == 0 else f"{self.bottom_center_x} + {offset}"
            case PosAnchor.BOTTOM_RIGHT:
                return self.bottom_right_x_fmt.format(padding=self.padding + offset)

    def get_y_expr(self, offset: float = 0):
        match self.anchor:
            case PosAnchor.CENTER:
                return self.center_y if offset == 0 else f"{self.center_y} + {offset}"
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


def get_file_format_ext(ext: str):
    match ext:
        case "ts":
            return "ts"
        case _:
            return "mp4"
