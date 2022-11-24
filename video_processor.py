import os
import ffmpeg
import pathlib
import subprocess
from pytube import YouTube, StreamQuery
from powerhour import *

interstitial_filename = "interstitial"
video_tmp_filename = "video.mp4"
audio_tmp_filename = "audio.mp3"

song_title_pos = VideoPos(anchor=PosAnchor.BOTTOM_LEFT, padding=100)
song_number_pos = VideoPos(anchor=PosAnchor.BOTTOM_RIGHT, padding=100)
interstitial_text_pos = VideoPos(anchor=PosAnchor.BOTTOM_CENTER, padding=100)

def download_song(config: PowerHourConfig, song: PowerHourSong):
    print(f"Starting Download {song.title} by {song.artist}")

    yt = YouTube(song.link)
    dir_path, file_path = get_paths(config, song)

    # download audio only
    print(f"Getting Audio Stream")
    astream = yt.streams.filter(only_audio=True, progressive=False).order_by("abr").last()
    print(f"Best Audio Stream {astream}")
    a_path = astream.download(output_path=dir_path, filename=audio_tmp_filename)

    # download video only
    print(f"Getting Video Stream")
    vstream = yt.streams.filter(only_video=True, progressive=False).order_by("resolution").last()
    print(f"Best Video Stream {vstream}")
    v_path = vstream.download(output_path=dir_path, filename=video_tmp_filename)
    return v_path, a_path


def process_song(config: PowerHourConfig, song: PowerHourSong, song_num: int, vid_path: str, aud_path: str,
                 remove: bool = True):
    dir_path, file_path = get_paths(config, song)
    audio = ffmpeg.input(aud_path)
    video = ffmpeg.input(vid_path)

    # dynamic values determined by both song and config params
    text_start_time = song.start_time + config.title_start_time
    text_end_time = song.start_time + config.title_duration
    fade_out_start_time = song.end_time - config.fade_duration
    enable_expr = f'between(t,{text_start_time},{text_end_time})'

    vid = (
        video
        .drawtext(text=song.artist, x=song_title_pos.get_x_expr(), y=song_title_pos.get_y_expr(),
                  enable=enable_expr,
                  fontfile=config.font_file,
                  fontsize=config.artist_font_size,
                  fontcolor=config.font_color,
                  bordercolor=config.font_border_color,
                  borderw=config.font_border_width)
        .drawtext(text=song.title, x=song_title_pos.get_x_expr(), y=song_title_pos.get_y_expr(config.artist_font_size * 1.2),
                  enable=enable_expr,
                  fontfile=config.font_file,
                  fontsize=config.title_font_size,
                  fontcolor=config.font_color,
                  bordercolor=config.font_border_color,
                  borderw=config.font_border_width)
        .drawtext(text=song_num, x=song_number_pos.get_x_expr(), y=song_number_pos.get_y_expr(),
                  fontfile=config.font_file,
                  fontsize=config.number_font_size,
                  fontcolor=config.font_color,
                  bordercolor=config.font_border_color,
                  borderw=config.font_border_width)
        .trim(start=song.start_time, end=song.end_time)
        .filter('fade', type="in", start_time=song.start_time, duration=config.fade_duration)
        .filter('fade', type="out", start_time=fade_out_start_time, duration=config.fade_duration)
        .setpts('PTS-STARTPTS')
    )
    aud = (
        audio
        .filter_('atrim', start=song.start_time, end=song.end_time)
        .filter('afade', type="in", start_time=song.start_time, duration=config.fade_duration)
        .filter('afade', type="out", start_time=fade_out_start_time, duration=config.fade_duration)
        .filter_('asetpts', 'PTS-STARTPTS')
    )
    print("outputting")
    command = ffmpeg.output(vid, aud, file_path)
    # ffmpeg.output(audio, video, file_path).run(overwrite_output=True)cc
    command.run(overwrite_output=True)
    if remove:
        os.remove(vid_path)
        os.remove(aud_path)


def process_interstitial(config: PowerHourConfig, interstitial_path: str):
    dir_path = get_dir_path(config)
    output_path = os.path.join(dir_path, f"{interstitial_filename}_{config.project_name}.ts")

    metadata = ffmpeg.probe(interstitial_path)
    video_stream = next((stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None)
    duration = video_stream['duration']
    fade_out_start_time = float(duration) - config.fade_duration
    text_start_time = 0.5
    enable_expr = f'between(t,{text_start_time},{fade_out_start_time})'
    interstitial = ffmpeg.input(interstitial_path)
    video = (
        interstitial
        .drawtext(text=config.interstitial_text,
                  x=interstitial_text_pos.get_x_expr(10), y=interstitial_text_pos.get_y_expr(10),
                  enable=enable_expr,
                  fontfile=config.font_file,
                  fontsize=config.interstitial_font_size * 1.1,
                  fontcolor="yellow")
        .drawtext(text=config.interstitial_text,
                  x=interstitial_text_pos.get_x_expr(), y=interstitial_text_pos.get_y_expr(),
                  enable=enable_expr,
                  fontfile=config.font_file,
                  fontsize=config.interstitial_font_size,
                  fontcolor=config.font_color,
                  bordercolor=config.font_border_color,
                  borderw=config.font_border_width)
        .filter('fade', type="in", start_time=0, duration=config.fade_duration)
        .filter('fade', type="out", start_time=fade_out_start_time, duration=config.fade_duration)
        .setpts('PTS-STARTPTS')
    )
    audio = (
        interstitial.audio
        .filter('afade', type="in", start_time=0, duration=config.fade_duration)
        .filter('afade', type="out", start_time=fade_out_start_time, duration=config.fade_duration)
        .filter_('asetpts', 'PTS-STARTPTS')
    )
    ffmpeg.output(video, audio, output_path).run(overwrite_output=True)
    return output_path


def convert_to_ts(vid_path: str):
    if not os.path.exists(vid_path):
        return
    pre, ext = os.path.splitext(vid_path)
    file_path = pre+'.ts'
    cmd = f"ffmpeg -y -i {vid_path} -c copy -bsf:v h264_mp4toannexb -f mpegts {file_path}"
    subprocess.run(cmd, stdout=subprocess.PIPE, check=True, shell=True)
    return file_path


def get_dir_path(config: PowerHourConfig):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.join(dir_path, config.project_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    return dir_path


def get_paths(config: PowerHourConfig, song: PowerHourSong):
    dir_path = get_dir_path(config)
    file_path = os.path.join(dir_path, song.get_filename())
    return dir_path, file_path


def validate_existing_files(config: PowerHourConfig, song: PowerHourSong):
    dir_path, file_path = get_paths(config, song)
    aud_path = os.path.join(dir_path, audio_tmp_filename)
    vid_path = os.path.join(dir_path, video_tmp_filename)
    if os.path.exists(aud_path) and os.path.exists(vid_path):
        print(vid_path)
        print(aud_path)
        return True, vid_path, aud_path
    else:
        return False


def get_highest_resolution(stream: StreamQuery):
    return stream.filter(adaptive=True).order_by("resolution").last()
