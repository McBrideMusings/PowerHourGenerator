import os
import sys
import argparse
from typing import Tuple

import phgen.input_parser
import phgen.video_processor
import phgen.main
import phgen.generate
from phgen.phconfig import PowerHourConfig

range_partition_chars = ['-', ':']


def main():
    parser = argparse.ArgumentParser(description=main.__doc__)
    args = parse_args(parser)
    songs = []
    inputType = 0
    if args.input.startswith("http"):
        inputType = 1
        songs = phgen.input_parser.parse_youtube(args)
    elif args.input.endswith(".csv") or args.input.endswith(".tsv"):
        inputType = 2
        songs = phgen.input_parser.parse_list(args)
    elif args.input.endswith(".mp4"):
        inputType = 3
        songs = phgen.input_parser.parse_video_file(args)

    if not songs or len(songs) == 0:
        print("Problem parsing input, no songs found or invalid input type")
        sys.exit(1)
    start, length = validate_range(args.range, songs)
    if args.dry_run:
        phgen.generate.generate_dry_run(songs, start, length)
        sys.exit(0)
    config = PowerHourConfig(args.project, target_res=args.resolution, font_file=args.font)
    if inputType == 1: # url
        phgen.generate.generate_http(config, songs[0], 0, no_text=args.no_text, no_fade=args.no_fade, no_clip=args.no_clip)
    elif inputType == 2: # list
        phgen.generate.generate_list(songs, config, start, length, no_text=args.no_text, no_fade=args.no_fade, no_clip=args.no_clip)
    elif inputType == 3: # video file
        phgen.generate.generate_video(config, songs[0], 0, no_text=args.no_text, no_fade=args.no_fade, no_clip=args.no_clip)
    else:
        print("Invalid input type, how did you even get here?")
        sys.exit(1)

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
        "-f",
        "--font",
        default="Oswald.ttf",
        help=(
            """\
                Font file to use for text
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
        "-t",
        "--title",
        default="Default Title",
        help=(
            """\
                Title if processing a single video or link
            """
        ),
    )
    parser.add_argument(
        "-a",
        "--artist",
        default="Default Artist",
        help=(
            """\
                Artist if processing a single video or link
            """
        ),
    )
    parser.add_argument(
        "-st",
        "--start_time",
        default=0,
        help=(
            """\
                Start time if processing a single video or link
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
    valid_path = os.path.exists(args.input)
    valid_url = args.input.startswith("http") # obviously not a perfect check, whatever dig your own grave user
    if not valid_path and not valid_url:
        print("input not valid path or youtube url")
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
                length = 1
        except:
            print("Something went wrong with parsing your range")
    start = start if 0 <= start < list_len else 0
    length = length if 0 < length < list_len - start else list_len - start
    return start, length