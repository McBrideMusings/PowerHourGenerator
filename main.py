import os
import argparse
import list_processor
import video_processor
from powerhour import PowerHourConfig


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--x', type=int, required=True)
    parser.add_argument('--y', type=int, required=True)
    args = parser.parse_args()


def main(input_path: str, output_name: str, verbose=False):
    songs = list_processor.parse_list(input_path)
    config = PowerHourConfig(output_name)
    for song in songs:
        if verbose:
            print(f"Song Parsed: {song} ")
    vid_path, aud_path = video_processor.download_song(config, songs[0])
    video_processor.process_media(config, songs[0], vid_path, aud_path)


# Put IDE Debug stuff here
if __name__ == "__main__":
    main("test_import.csv", "test", True)
