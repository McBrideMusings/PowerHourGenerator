import os
import csv
from phgen.powerhour import PowerHourSong
from datetime import datetime, timedelta


def parse_list(path: str):
    pre, ext = os.path.splitext(path)
    song_list: list = []
    with open(path) as textFile:
        reader = csv.reader(textFile) if ext == "csv" else csv.reader(textFile, delimiter='\t')
        for row in reader:
            parsed = PowerHourSong(
                row[0].strip(),  # title
                row[1].strip(),  # artist
                parse_time(row[2]).seconds,  # start time
                row[3])  # url
            song_list.append(parsed)
            print(parsed)
    return song_list


def parse_time(time: str):
    t = datetime.strptime(time, "%M:%S")
    return timedelta(minutes=t.minute, seconds=t.second)