import os
import argparse
import list_processor
import video_processor
import uuid
from powerhour import PowerHourConfig

test_import_csv: str = "test_import.csv"
test_import_tsv: str = "test_import.tsv"
test_interstitial: str = "test_interstitial.ts"
test_process: str = "test_process.ts"

test_padding_x = 100
test_padding_y = 100


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--x', type=int, required=True)
    parser.add_argument('--y', type=int, required=True)
    args = parser.parse_args()


def main(input_path: str, project_name: str, interstitial_path: str, song_limit: int = 0):
    main_songs = list_processor.parse_list(input_path)
    main_config = PowerHourConfig(project_name)
    # Concat doesn't work right now, no need to process the interstitial
    # interstitial_processed = video_processor.process_interstitial(main_config, interstitial_path)
    num = 1
    song_path_list = []
    if 0 < song_limit < len(main_songs):
        main_songs = main_songs[:song_limit]
    print(f"song length {len(main_songs)}")
    for song in main_songs:
        song_path = video_processor.download_song(main_config, song)
        song_path = video_processor.process_song_effects(main_config, song, num, song_path)
        song_path_list.append(song_path)
        num = num + 1
    # Concat doesn't work well right now
    # video_processor.concat_power_hour(main_config, interstitial_processed, song_path_list)


# Put IDE Debug stuff here
if __name__ == "__main__":
    if os.getenv("PARSE_ONLY") is not None:
        print(f"PARSE_ONLY")
        songs = list_processor.parse_list(test_import_tsv)
    elif os.getenv("DOWNLOAD_ONLY") is not None:
        print(f"DOWNLOAD_ONLY")
        config = PowerHourConfig(str(uuid.uuid4()), text_padding_x=test_padding_x, text_padding_y=test_padding_y)
        songs = list_processor.parse_list(test_import_tsv)
        vid_path = video_processor.download_song(config, songs[1], False)
    elif os.getenv("PROCESS_ONLY") is not None:
        print(f"PROCESS_ONLY")
        config = PowerHourConfig(str(uuid.uuid4()), text_padding_x=test_padding_x, text_padding_y=test_padding_y)
        songs = list_processor.parse_list(test_import_tsv)
        video_processor.process_song_effects(config, songs[0], 1, test_process, False)
    elif os.getenv("AD_HOC") is not None:
        # Put whatever you need to test here
        print(f"AD_HOC")
        # config = PowerHourConfig(str(uuid.uuid4()), text_padding_x=test_padding_x, text_padding_y=test_padding_y)
        # songs = list_processor.parse_list(test_import_tsv)
        # songs_paths = ["Heybaby.NoDoubt.clipped.ts", "Pictureinmymind.PinkPantheress,SamGellaitry.clipped.ts"]
        # video_processor.concat_power_hour(config, "", songs_paths)
    else:
        print(f"MAIN")
        config = PowerHourConfig(str(uuid.uuid4()), text_padding_x=test_padding_x, text_padding_y=test_padding_y)
        songs = list_processor.parse_list(test_import_tsv)
        env_song_limit = 0
        if os.getenv("SONG_LIMIT") is not None:
            env_song_limit = int(os.getenv("SONG_LIMIT"))
        main(test_import_tsv, str(uuid.uuid4()), test_interstitial, env_song_limit)

