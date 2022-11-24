import os
import argparse
import list_processor
import video_processor
from powerhour import PowerHourConfig

test_import_csv: str = "test_import.csv"
test_folder: str = "test"


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
    video_processor.process_media(config, songs[0], 1, vid_path, aud_path)


# Put IDE Debug stuff here
if __name__ == "__main__":
    if os.getenv("DOWNLOAD_ONLY") is not None:
        print(f"DOWNLOAD_ONLY")
        songs = list_processor.parse_list(test_import_csv)
        config = PowerHourConfig(test_folder)
        vid_path, aud_path = video_processor.download_song(config, songs[0])
    elif os.getenv("PROCESS_ONLY") is not None:
        print(f"PROCESS_ONLY")
        songs = list_processor.parse_list(test_import_csv)
        config = PowerHourConfig(test_folder, text_padding_x=100, text_padding_y=80)
        valid, vid_path, aud_path = video_processor.validate_existing_files(config, songs[0])
        if valid:
            video_processor.process_media(config, songs[0], 1, vid_path, aud_path, False)
        else:
            print("video or audio path does not exist, download_only first")
    else:
        main(test_import_csv, test_folder, True)
