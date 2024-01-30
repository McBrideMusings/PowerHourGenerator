import os
import csv
import argparse
from datetime import datetime, timedelta
from phgen.phsong import PowerHourSong
from pytube import YouTube


title_key : str = "title"
artist_key : str = "artist"
start_time_key : str = "start_time"
duration_key : str = "duration"
link_key : str = "link"
name_key : str = "name"


def parse_input(args: argparse.Namespace):
    if args.input.startswith("http"):
        return parse_youtube(args)
    elif args.input.endswith(".csv") or args.input.endswith(".tsv"):
        return parse_list(args)
    elif args.input.endswith(".mp4"):
        return parse_video_file(args)
    else:
        print("Invalid input file type")
        return []


def parse_youtube(args: argparse.Namespace):
    song_list: list = []
    try:
        yt = YouTube(args.input, use_oauth=True)
        title = args.title if args.title else yt.title
        artist = args.artist if args.artist else yt.author
        start_time = args.start_time if args.start_time else 0
        song_list.append(PowerHourSong(title=title, artist=artist, start_time=start_time, link=args.input, name=args.name))
    except Exception as e:
        print(e)
    return song_list


def parse_video_file(args: argparse.Namespace):
    return [PowerHourSong(title=args.title, artist=args.artist, start_time=args.start_time, link=args.input, name=args.name)]


def parse_list(args: argparse.Namespace):
    pre, ext = os.path.splitext(args.input)
    song_list: list = []
    with open(args.input, 'r', encoding='utf-8') as textFile:
        reader = csv.DictReader(textFile) if ext == "csv" else csv.DictReader(textFile, delimiter='\t')
        for row in reader:
            if link_key not in row:
                print("Row missing link!")
                continue
            link = row[link_key]
            title = row[title_key] if title_key in row else "NaN"
            artist = row[artist_key] if artist_key in row else "NaN"
            name = row[name_key] if name_key in row else ""
            start_time = row[start_time_key] if start_time_key in row else "0"
            start_time = parse_time(start_time, 0).seconds
            duration = row[duration_key] if duration_key in row else "60"
            duration = parse_time(duration, 60).seconds
            parsed = PowerHourSong(
                title=title.strip(),
                artist=artist.strip(),
                start_time=start_time,
                duration=duration,
                name=name.strip(),
                link=link)
            song_list.append(parsed)
    if len(song_list) == 0:
        print("No songs found in list!")
    return song_list


def parse_time(time: str, default_result: int) -> timedelta:
    try:
        if not time:
            return timedelta(seconds=default_result)
        if ':' not in time:
            return timedelta(seconds=int(time))
        else:
            t = datetime.strptime(time, "%M:%S")
            return timedelta(minutes=t.minute, seconds=t.second)
    except Exception as e:
        print(e)
        return timedelta(seconds=default_result)
