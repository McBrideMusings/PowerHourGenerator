import os
import sys
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


def main_args():
    parser = argparse.ArgumentParser(description=main.__doc__)
    args = parse_args()
    if not args.input or os.path.exists(args.input):
        parser.print_help()
        sys.exit(1)
    else:
        project = args.project
        if project is None:
            project = str(uuid.uuid4())
        main(args.input, args.project, args.resolution, args.limit)


def main(input_path: str, project_name: str, target_res: str = "1080p", song_limit: int = 0, start: int = 1):
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
        if num >= start:
            song_path = video_processor.download_song(main_config, song)
            scale, letterbox = video_processor.should_scale_letterbox(target_res, song_path)
            if scale or letterbox:
                song_path = video_processor.scale_letterbox_video(scale, letterbox, target_res, song_path)
            song_path = video_processor.process_song_effects(main_config, song, num, song_path)
            path, filename = os.path.split(song_path)
            filename = os.path.splitext(filename)[0]
            newfilename = f"{project_name}.{num:02d}.{song.get_filename('mp4')}"
            newpath = os.path.join(path, newfilename)
            os.rename(song_path, newpath)
            song_path_list.append(song_path)
        num = num + 1
    # Concat doesn't work correctly right now
    # video_processor.concat_power_hour(main_config, interstitial_processed, song_path_list)


def parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    parser.add_argument(
        "-i",
        "--input",
        help=(
            "Path to a formatted csv or tsv"
            "Required, enter -example to generate an example file"
        ),
    )
    parser.add_argument(
        "-p",
        "--project",
        help=(
            "Name of the video project"
            "Will generate a folder with this name and will be used in file names"
        ),
    )
    parser.add_argument(
        "-r",
        "--resolution",
        const="mp4",
        help=(
            "Resolution of the project, eg 1080p, 720p"
            "All videos will be scaled to this resolution, letterboxed if necessary"
        ),
    )
    parser.add_argument(
        "-l",
        "--limit",
        const="0",
        help=(
            "Number of songs to download and process, starting from the first"
            "Defaults to downloading the entire input"
        ),
    )
    return parser.parse_args()


# Put IDE Debug stuff here
if __name__ == "__main__":
    if os.getenv("PARSE_ONLY") is not None:
        print(f"PARSE_ONLY")
        songs = list_processor.parse_list(test_import_tsv)
    elif os.getenv("DOWNLOAD_ONLY") is not None:
        print(f"DOWNLOAD_ONLY")
        config = PowerHourConfig(str(uuid.uuid4()), text_padding_x=test_padding_x, text_padding_y=test_padding_y)
        songs = list_processor.parse_list(test_import_tsv)
        for song in songs:
            video_processor.download_song(config, song)
    elif os.getenv("PROCESS_ONLY") is not None:
        print(f"PROCESS_ONLY")
        config = PowerHourConfig(str(uuid.uuid4()), text_padding_x=test_padding_x, text_padding_y=test_padding_y)
        songs = list_processor.parse_list(test_import_tsv)
        video_processor.process_song_effects(config, songs[0], 1, test_process, False)
    elif os.getenv("AD_HOC") is not None:
        # Put whatever you need to test here
        print(f"AD_HOC")
        video_processor.scale_letterbox_video(True, True, "1080p", "Aaron'sParty.AaronCarter.clipped.mp4")
    else:
        print(f"MAIN")
        config = PowerHourConfig(str(uuid.uuid4()), text_padding_x=test_padding_x, text_padding_y=test_padding_y)
        songs = list_processor.parse_list(test_import_tsv)
        env_song_limit = 0
        if os.getenv("SONG_LIMIT") is not None:
            env_song_limit = int(os.getenv("SONG_LIMIT"))
        main(test_import_tsv, str(uuid.uuid4()), target_res="1080p", song_limit=env_song_limit)
