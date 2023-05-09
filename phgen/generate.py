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

def process_video(song_path: str, config : PowerHourConfig, song : PowerHourSong, num : int, remove : bool=True, no_fade: bool=False, no_text: bool=False):
    scale, letterbox = phgen.video_processor.should_scale_letterbox(config.target_res, song_path)
    if scale or letterbox:
        song_path = phgen.video_processor.scale_letterbox_video(scale, letterbox, config.target_res, song_path, remove=remove)
    if not no_fade and not no_text:
        add_fade = not no_fade
        add_text = not no_text
        song_path = phgen.video_processor.process_song_effects(config, song, num, song_path, add_fade=add_fade,
                                                               add_text=add_text, remove=remove)
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

def generate(songs: list, config: PowerHourConfig, start: int, length: int, no_text: bool=False, no_fade: bool=False, no_clip: bool=False):
    for i, song in enumerate(songs):
        if i < start or i >= (start + length):
            continue
        try:
            num = i + 1
            clip = not no_clip
            song_path = phgen.video_processor.download_song(config, song, clip=clip)
            song_path = process_video(song_path, config, song, num, no_fade=no_fade, no_text=no_text)
            create_file(song_path, config, song, num)
        except Exception as e:
            print(f"Error on row {i} {song} - {e}")



