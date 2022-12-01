import os
import sys
import argparse
from typing import Tuple
import list_processor, video_processor
import uuid
from powerhour import PowerHourConfig, ProcessOpt

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


def main(input_path: str, project_name: str, input_range: Tuple[int, int] = (-1, -1), target_res: str = "1080p",
         process: ProcessOpt = ProcessOpt.EDITSCALEFX):
    main_songs = list_processor.parse_list(input_path)
    main_config = PowerHourConfig(project_name)
    # Concat doesn't work right now, no need to process the interstitial
    # interstitial_processed = video_processor.process_interstitial(main_config, interstitial_path)
    num = 1
    song_path_list = []
    start = 0
    length = len(main_songs)
    if input_range[0] > -1:
        start = input_range[0]
    if start + input_range[1] < length:
        length = input_range[1]
    if start >= 0:
        if length < 0:
            main_songs = main_songs[start:]
        if length > 0 and length + start < len(main_songs):
            main_songs = main_songs[start:start+length]
    print(f"process length {len(main_songs)}")
    for song in main_songs:
        try:
            song_path = video_processor.download_song(main_config, song)
            if process >= 1:
                scale, letterbox = video_processor.should_scale_letterbox(target_res, song_path)
                if process >= 2 and (scale or letterbox):
                    song_path = video_processor.scale_letterbox_video(scale, letterbox, target_res, song_path)
                if process >= 3:
                    song_path = video_processor.process_song_effects(main_config, song, num, song_path)
            path, _ = os.path.split(song_path)
            newpath = os.path.join(path, main_config.get_ph_filename(num, song))
            os.rename(song_path, newpath)
            song_path_list.append(song_path)
        except:
            print(f"Error on row {num}")
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
        "-res",
        "--resolution",
        const="mp4",
        help=(
            "Resolution of the project, eg 1080p, 720p"
            "All videos will be scaled to this resolution, letterboxed if necessary"
        ),
    )
    parser.add_argument(
        "-rng",
        "--range",
        help=(
            "Number of songs to download and process, starting from the first"
            "Defaults to downloading the entire input"
        ),
    )
    parser.add_argument(
        "-l",
        "--link",
        help=(
            "Number of songs to download and process, starting from the first"
            "Defaults to downloading the entire input"
        ),
    )
    return parser.parse_args()


def parse_range(range_input: str):
    if not range_input:
        return -1
    try:
        if '-' in range_input:
            part = range_input.partition('-')
            start = int(part[0])
            length = int(part[2])
            return start, length
        else:
            start = int(range_input)
            return start, -1
    except:
        print("Something went wrong")
    finally:
        return -1


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
    elif os.getenv("AD_HOC") is not None:
        # Put whatever you need to test here
        print(f"AD_HOC")
        config = PowerHourConfig(str(uuid.uuid4()), text_padding_x=test_padding_x, text_padding_y=test_padding_y)
        songs = list_processor.parse_list(test_import_tsv)
        main(test_import_tsv, "bdog", input_range=(0, 1), process=ProcessOpt.EDITSCALE)
    else:
        print(f"MAIN")
        config = PowerHourConfig(str(uuid.uuid4()), text_padding_x=test_padding_x, text_padding_y=test_padding_y)
        songs = list_processor.parse_list(test_import_tsv)
        env_song_limit = 0
        if os.getenv("SONG_LIMIT") is not None:
            upper = int(os.getenv("SONG_LIMIT"))
            main(test_import_tsv, str(uuid.uuid4()), input_range=(-1, upper))
        if os.getenv("PROCESS_OPT") is not None:
            opt = int(os.getenv("PROCESS_OPT"))
            main(test_import_tsv, str(uuid.uuid4()), process=opt)
        main(test_import_tsv, str(uuid.uuid4()))
