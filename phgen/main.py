import os
import phgen.input_parser
import phgen.video_processor
import phgen.generate
from phgen.phsong import PowerHourSong
from phgen.phconfig import PowerHourConfig

debug_tsv: str = "import.tsv"
debug_target_res: str = "1080p"
debug_config: PowerHourConfig = PowerHourConfig("", target_res=debug_target_res, font_file="Oswald.ttf")
debug_song: PowerHourSong = PowerHourSong("Go", "The Chemical Brothers", 0, "https://www.youtube.com/watch?v=LO2RPDZkY88")
debug_video: str = debug_song.get_filename("mp4", "clipped")

if __name__ == "__main__":
    print(f"0: Generate {debug_tsv}")
    print(f"1: Generate {debug_tsv} (Dry Run)")
    print(f"2: Generate {debug_tsv} First Index Only")
    print(f"3: Download Song {debug_song}")
    print(f"4: Process Video {debug_video}")
    num = int(input("Enter a number between 0 and 4: "))
    if num == 0:
        songs = phgen.input_parser.parse_input(debug_tsv)
        phgen.generate.generate_list(songs, debug_config, 0, len(songs))
    elif num == 1:
        songs = phgen.input_parser.parse_input(debug_tsv)
        phgen.generate.generate_dry_run(songs, 0, len(songs))
    elif num == 2:
        songs = phgen.input_parser.parse_input(debug_tsv)
        phgen.generate.generate_list(songs, debug_config, 0, 1)
    elif num == 3:
        phgen.video_processor.download(debug_config, debug_song)
    elif num == 4:
        dir_path = debug_config.get_dir_path()
        file_path = os.path.join(dir_path, debug_video)
        phgen.generate.process_video(file_path, debug_config, debug_song, 2, remove_src=False)
