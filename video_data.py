class StandardResolution:
    """A two-dimensional vector with Cartesian coordinates."""

    def __init__(self, key: str, size: (int, int)):
        self.key = key
        self.size = size
        self.width = size[0]
        self.height = size[1]

    def __str__(self):
        return self.key

    def __eq__(self, s):
        return s == self.key


resolution_default = 4
resolutions = [
    StandardResolution("144p", (256, 144)),
    StandardResolution("240p", (426, 240)),
    StandardResolution("360p", (480, 360)),
    StandardResolution("720p", (1280, 720)),
    StandardResolution("1080p", (1920, 1080)),
    StandardResolution("1440p", (2560, 1440)),
    StandardResolution("2160p", (3840, 2160)),
]


def validate_resolution(res: str):
    if not res or res not in resolutions:
        return resolutions[resolution_default].key
    return res


def get_resolution(width: int, height: int):
    for resolution in resolutions:
        if resolution.width == width and resolution.height == height:
            return resolution.key
    return "Unknown"


def get_pixel_size(res: str):
    """Get the pixel size

    :param str res:
        Video resolution i.e. "720p", "480p", "360p", "240p", "144p"
    :rtype: :(int, int) width, height or None
    :returns:
        tuple (int, int) width, height matching the given resolution key or None if
        not found.

    """
    for resolution in resolutions:
        if res == resolution:
            return resolution.size
    return -1, -1


def get_valid_resolution(res: str):
    if not res or res not in resolutions:
        return resolutions[resolution_default].key
    return res



