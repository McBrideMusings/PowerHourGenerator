import os
import ffmpeg
from pytube import YouTube, StreamQuery
from powerhour import *

interstitial_filename = "interstitial"

song_title_pos = VideoPos(anchor=PosAnchor.BOTTOM_LEFT, padding=100)
song_number_pos = VideoPos(anchor=PosAnchor.BOTTOM_RIGHT, padding=100)
interstitial_text_pos = VideoPos(anchor=PosAnchor.BOTTOM_CENTER, padding=100)


def download_song(config: PowerHourConfig, song: PowerHourSong, remove: bool = True):
    print(f"Starting Download {song.title} by {song.artist}")

    yt = YouTube(song.link)
    dir_path = get_dir_path(config)
    file_path = os.path.join(dir_path, song.get_filename("ts", "clipped"))

    # download audio only
    print(f"Getting Audio Stream")
    aud_stream = yt.streams.filter(only_audio=True, progressive=False).order_by("abr").last()
    print(f"Best Audio Stream {aud_stream}")
    aud_path = aud_stream.download(output_path=dir_path, filename="audio.mp4")

    # download video only
    print(f"Getting Video Stream")
    vid_stream = yt.streams.filter(only_video=True, progressive=False).order_by("resolution").last()
    print(f"Best Video Stream {vid_stream}")
    vid_path = vid_stream.download(output_path=dir_path, filename="video.mp4")
    print(f"{song.title} Streams Downloaded")
    # combine
    combine_audio_video(config, song, vid_path, aud_path)
    if remove:
        print(f"Removing Temporary Files for {song.title}")
        os.remove(vid_path)
        os.remove(aud_path)
    return file_path


def combine_audio_video(config: PowerHourConfig, song: PowerHourSong, vid_path: str, aud_path: str):
    dir_path = get_dir_path(config)
    file_path = os.path.join(dir_path, song.get_filename("ts", "clipped"))
    video = (
        ffmpeg.input(vid_path)
        .trim(start=song.start_time, end=song.end_time)
        .setpts('PTS-STARTPTS')
    )
    audio = (
        ffmpeg.input(aud_path)
        .filter_('atrim', start=song.start_time, end=song.end_time)
        .filter_('asetpts', 'PTS-STARTPTS')
    )
    # converting to Transport Stream as intermediary because it supports concat and mp4 does not
    # remove vcodec, format(f) and change path ending above if you want to switch to combine as mp4
    # ffmpeg -i file1.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts fileIntermediate1.ts
    ffmpeg.output(audio, video, file_path, vcodec="libx264", f="mpegts").run(overwrite_output=True)
    print(f"ffmpeg combine_audio_video output complete")
    return file_path


def process_song_effects(config: PowerHourConfig, song: PowerHourSong, num: int, vid_path: str, remove: bool = True):
    dir_path = get_dir_path(config)
    file_path = os.path.join(dir_path, song.get_filename("ts", "effects"))

    ffmpeg_input = ffmpeg.input(vid_path)
    # dynamic values determined by both song and config params
    title_start_time = config.title_start_time
    title_end_time = title_start_time + config.title_duration
    fade_out_start_time = 60 - config.fade_duration
    enable_expr = f'between(t,{title_start_time},{title_end_time})'
    song_num_str = str(num) if num != 60 else "60!"  # ╰(*°▽°*)╯
    video = (
        ffmpeg_input.video
        .drawtext(text=song.artist,
                  x=song_title_pos.get_x_expr(),
                  y=song_title_pos.get_y_expr(),
                  enable=enable_expr,
                  fontfile=config.font_file,
                  fontsize=config.artist_font_size,
                  fontcolor=config.font_color,
                  bordercolor=config.font_border_color,
                  borderw=config.font_border_width)
        .drawtext(text=song.title,
                  x=song_title_pos.get_x_expr(),
                  y=song_title_pos.get_y_expr(config.artist_font_size * 1.2),
                  enable=enable_expr,
                  fontfile=config.font_file,
                  fontsize=config.title_font_size,
                  fontcolor=config.font_color,
                  bordercolor=config.font_border_color,
                  borderw=config.font_border_width)
        .drawtext(text=song_num_str,
                  x=song_number_pos.get_x_expr(),
                  y=song_number_pos.get_y_expr(),
                  fontfile=config.font_file,
                  fontsize=config.number_font_size,
                  fontcolor=config.font_color,
                  bordercolor=config.font_border_color,
                  borderw=config.font_border_width)
        .filter('fade', type="in", duration=config.fade_duration)
        .filter('fade', type="out", start_time=fade_out_start_time, duration=config.fade_duration)
        .setpts('PTS-STARTPTS')
    )
    audio = (
        ffmpeg_input.audio
        .filter('afade', type="in", duration=config.fade_duration)
        .filter('afade', type="out", start_time=fade_out_start_time, duration=config.fade_duration)
        .filter_('asetpts', 'PTS-STARTPTS')
    )
    ffmpeg.output(audio, video, file_path).run(overwrite_output=True)
    print(f"ffmpeg process_song_effects output complete")
    if remove:
        os.remove(vid_path)


def process_interstitial(config: PowerHourConfig, interstitial_path: str):
    dir_path = get_dir_path(config)
    output_path = os.path.join(dir_path, f"{interstitial_filename}_{config.project_name}.ts")

    metadata = ffmpeg.probe(interstitial_path)
    video_stream = next((stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None)
    duration = video_stream['duration']
    fade_out_start_time = float(duration) - config.fade_duration
    text_start_time = duration * 0.1  # 1/10th into the video
    enable_expr = f'between(t,{text_start_time},{fade_out_start_time})'
    interstitial = ffmpeg.input(interstitial_path)
    video = (
        interstitial.video
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


def concat_power_hour(config: PowerHourConfig, interstitial_path: str, *video_paths: str):
    if not os.path.exists(interstitial_path):
        return
    dir_path = get_dir_path(config)
    output_path = os.path.join(dir_path, f"{config.project_name}_output.mp4")
    txt_path = 'tmp.txt'
    with open(txt_path, 'w') as f:
        for video_path in video_paths:
            f.write(f"file {video_path}\n")
            f.write(f"file {interstitial_path}\n")
    # ffmpeg -f concat -safe 0 -i tmp.txt -c copy output.mp4
    ffmpeg.input(txt_path, f='concat', safe='0').output(output_path, vcodec='libx264').run(overwrite_output=True)
    os.remove(txt_path)


def get_dir_path(config: PowerHourConfig):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.join(dir_path, config.project_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    return dir_path


def get_highest_resolution(stream: StreamQuery):
    return stream.filter(adaptive=True).order_by("resolution").last()
