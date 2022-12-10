import os
import csv
from datetime import datetime, timedelta
import phgen.video_processor
from phgen.phsong import PowerHourSong


title_key : str = "title"
artist_key : str = "artist"
start_time_key : str = "start_time"
duration_key : str = "duration"
link_key : str = "link"


def parse_list(path: str):
    pre, ext = os.path.splitext(path)
    song_list: list = []
    with open(path) as textFile:
        # TODO Latin characters like Í in ROSALÍA result in charparse error here. Fix that w/o losing the accent
        reader = csv.DictReader(textFile) if ext == "csv" else csv.DictReader(textFile, delimiter='\t')
        for row in reader:
            if link_key not in row:
                print("Row missing link!")
                continue
            link = row[link_key]
            title = row[title_key] if title_key in row else "NaN"
            artist = row[artist_key] if artist_key in row else "NaN"
            start_time = row[start_time_key] if start_time_key in row else "0"
            start_time = parse_time(start_time, 0).seconds
            duration = row[duration_key] if duration_key in row else "60"
            duration = parse_time(duration, 60).seconds
            parsed = PowerHourSong(
                title=title.strip(),
                artist=artist.strip(),
                start_time=start_time,
                duration=duration,
                link=link)
            song_list.append(parsed)
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
