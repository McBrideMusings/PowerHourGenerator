import os
import uuid
from typing import Tuple
import phgen.input_parser
import phgen.video_processor
from phgen.phsong import PowerHourSong
from phgen.phprocess import ProcessOpt
from phgen.phconfig import PowerHourConfig

if __name__ == "__main__":
    test_path = r"C:\Users\pierc\Downloads\ph04\EverytimeWeTouch.Cascada.clipped.scaled.mp4"
    test_tsv_path = r"C:\Users\pierc\Downloads\test_short_dur.tsv"
    config = PowerHourConfig("test")
    songs = phgen.input_parser.parse_list(test_tsv_path)
    phgen.video_processor.process_song_effects(config, songs[0], 1, test_path, remove=False)
