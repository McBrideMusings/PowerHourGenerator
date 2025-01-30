import os
import phgen.input_parser
import phgen.video_processor
from phgen.phsong import PowerHourSong
from phgen.phconfig import PowerHourConfig

def search_file(directory : str, file_name : str):
    for root, dirs, files in os.walk(directory):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

def process_video(song_path: str, config : PowerHourConfig, song : PowerHourSong, num : int, remove_src : bool=True, remove_mid : bool=True, no_fade: bool=False, no_text: bool=False):
    scale, letterbox = phgen.video_processor.should_scale_letterbox(config.target_res, song_path)
    if scale or letterbox:
        song_path = phgen.video_processor.scale_letterbox_video(scale, letterbox, config.target_res, song_path, remove=remove_src)
    if not no_fade and not no_text:
        add_fade = not no_fade
        add_text = not no_text
        song_path = phgen.video_processor.process_song_effects(config, song, num, song_path, add_fade=add_fade,
                                                               add_text=add_text, remove=remove_mid)
    return song_path

def create_file(song_path: str, config : PowerHourConfig, song : PowerHourSong, num : int, remove: bool=True) -> str:
    path, _ = os.path.split(song_path)
    new_path = os.path.join(path, config.get_ph_filename(num, song))
    if os.path.isfile(new_path):
        os.remove(new_path)
    os.rename(song_path, new_path)
    return new_path

def generate_dry_run(songs, start, length):
    print(f"Parsed Song Length {length}")
    for i, song in enumerate(songs):
        if i < start or i >= (start + length):
            continue
        print(song)

def generate_list(songs: list, config: PowerHourConfig, start: int, length: int, no_text: bool=False, no_fade: bool=False, no_clip: bool=False):
    for i, song in enumerate(songs):
        if i < start or i >= (start + length):
            continue
        try:
            # TODO Possibly add a way to check if the link is a path or url? (TBD)
            if song.uri.startswith("http"):
                generate_http(config, song, i+1, no_text=no_text, no_fade=no_fade, no_clip=no_clip)
            else:
                generate_video(config, song, i+1, no_text=no_text, no_fade=no_fade, no_clip=no_clip)
        except Exception as e:
            print(f"Error on row {i} {song} - {e}")

def generate_video(config : PowerHourConfig, song : PowerHourSong, num : int, no_text: bool=False, no_fade: bool=False, no_clip: bool=False, remove: bool=True):
    try:
        if not no_clip:
            video_path = phgen.video_processor.clip(config, song, song.uri, remove=False)
        video_path = process_video(video_path, config, song, num, no_fade=no_fade, no_text=no_text, remove_src=remove)
        create_file(video_path, config, song, num)
    except Exception as e:
        raise Exception(e)

def generate_http(config : PowerHourConfig, song : PowerHourSong, num : int, no_text: bool=False, no_fade: bool=False, no_clip: bool=False, remove: bool=True):
    try:
        video_path = phgen.video_processor.download(config, song)
        if not no_clip:
            video_path = phgen.video_processor.clip(config, song, video_path)
        video_path = process_video(video_path, config, song, num, no_fade=no_fade, no_text=no_text, remove_src=remove)
        create_file(video_path, config, song, num)
    except Exception as e:
        raise Exception(e)



