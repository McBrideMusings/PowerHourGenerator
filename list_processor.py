import csv
from powerhour import PowerHourSong
from datetime import datetime, timedelta


def parse_list(path: str):
    list = []
    with open(path) as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            parsed = PowerHourSong(
                row[0].strip(),
                row[1].strip(),
                parse_time(row[2]).seconds,
                row[3])
            list.append(parsed)
    return list


def parse_time(time: str):
    t = datetime.strptime(time, "%M:%S")
    return timedelta(minutes=t.minute, seconds=t.second)