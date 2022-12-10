import os
import sys
import argparse
from typing import Tuple

import phgen.input_parser
import phgen.video_processor
import phgen.main
from phgen.phconfig import PowerHourConfig

range_partition_chars = ['-', ':']


def main():
    parser = argparse.ArgumentParser(description=main.__doc__)
    args = parse_args(parser)
    songs = phgen.input_parser.parse_list(args.input)
    start, length = validate_range(args.range, songs)
    if args.dry_run:
        print(f"Parsed Song Length {length}")
        for i, song in enumerate(songs):
            if i < start or i >= (start + length):
                continue
            print(song)
        sys.exit(0)
    config = PowerHourConfig(args.project, target_res=args.resolution)
    for i, song in enumerate(songs):
        if i < start or i >= (start + length):
            continue
        try:
            num = i + 1
            clip = not args.no_clip
            song_path = phgen.video_processor.download_song(config, song, clip=clip)
            scale, letterbox = phgen.video_processor.should_scale_letterbox(config.target_res, song_path)
            if scale or letterbox:
                song_path = phgen.video_processor.scale_letterbox_video(scale, letterbox, config.target_res, song_path)
            if not args.no_fade and not args.no_text:
                add_fade = not args.no_fade
                add_text = not args.no_text
                song_path = phgen.video_processor.process_song_effects(config, song, num, song_path, add_fade=add_fade,
                                                                       add_text=add_text)
            path, _ = os.path.split(song_path)
            new_path = os.path.join(path, config.get_ph_filename(num, song))
            os.rename(song_path, new_path)
        except Exception as e:
            print(f"Error on row {i}")
            print(e)


def parse_args(parser: argparse.ArgumentParser) -> argparse.Namespace:
    parser.add_argument(
        "input",
        nargs='?',
        help=(
            """\
                Path to a formatted csv, tsv, or a youtube url to download (TBD)
                Required, enter -example to generate an example tsv (TBD)
            """
        ),
    )
    parser.add_argument(
        "-p",
        "--project",
        help=(
            """\
                Name of the video project
                Will generate a folder with this name and will be used in file names
            """
        ),
    )
    parser.add_argument(
        "-res",
        "--resolution",
        default="1080p",
        help=(
            """\
                Resolution of the project, eg 1080p, 720p
                All videos will be scaled to this resolution, letterboxed if necessary
            """
        ),
    )
    parser.add_argument(
        "-r",
        "--range",
        help=(
            """\
                Range of the input list to process
                If just a number, will start at that index (starts with 0) and process the rest of the list.
                If formatted with 2 numbers with a valid delimiter (-, :)
                the first will be the starting index the second the length to process, including start
            """
        ),
    )
    parser.add_argument(
        "-d",
        "--dry_run",
        action="store_true",
        help=(
            """\
                Dry-run, will only parse input and print the parsed songs
            """
        ),
    )
    parser.add_argument(
        "-xt",
        "--no_text",
        action="store_true",
        help=(
            """\
                Don't add any text to the final output
            """
        ),
    )
    parser.add_argument(
        "-xf",
        "--no_fade",
        action="store_true",
        help=(
            """\
                Don't fade in and out on the final output
            """
        ),
    )
    parser.add_argument(
        "-xc",
        "--no_clip",
        action="store_true",
        help=(
            """\
                Don't clip the final output 
            """
        ),
    )
    args = parser.parse_args()
    if not args.input:
        parser.print_help()
        sys.exit(1)
    if not os.path.exists(args.input):
        print("input file doesn't exist, check again you spelled it right")
        sys.exit(1)
    valid_path = True
    if args.project is None:
        valid_path = False
        for num in range(1, 99):
            args.project = "ph{:02d}".format(num)
            if not os.path.exists(os.path.join(os.getcwd(), args.project)):
                valid_path = True
                break
    if not valid_path:
        print("Wow you've already created ph01-ph99 folders, holy shit just delete some my guy")
        sys.exit(1)
    return args


def validate_range(range_input: str, song_list: list) -> Tuple[int, int]:
    start = 0
    length = len(song_list)
    list_len = len(song_list)
    if range_input:
        try:
            part_char = ''
            for char in range_partition_chars:
                if char in range_input:
                    part_char = char
                    break
            if part_char:
                part = range_input.partition(part_char)
                start = int(part[0])
                length = int(part[2])
            else:
                start = int(range_input)
                length = list_len - start
        except:
            print("Something went wrong with parsing your range")
    start = start if 0 <= start < list_len else 0
    length = length if 0 < length < list_len - start else list_len - start
    return start, length
