import os
import ffmpeg
import phgen.ffmpeg_utilities
from phgen.ffmpeg_utilities import VideoPos, PosAnchor
import phgen.video_data
from phgen.phconfig import PowerHourSong, PowerHourConfig
from pytube import YouTube, StreamQuery

interstitial_filename = "interstitial"

song_title_pos = VideoPos(anchor=PosAnchor.BOTTOM_LEFT, padding=100)
song_number_pos = VideoPos(anchor=PosAnchor.BOTTOM_RIGHT, padding=100)
interstitial_text_pos = VideoPos(anchor=PosAnchor.BOTTOM_CENTER, padding=100)


def download(config: PowerHourConfig, song: PowerHourSong, ext: str = "mp4",
                  target_res: str = "1080p"):
    print(f"Starting Download {song.title} by {song.artist}")
    ext = phgen.ffmpeg_utilities.get_file_format_ext(ext)

    yt = YouTube(song.link, use_oauth=True)
    dir_path = config.get_dir_path()
    print(dir_path)
    file_path = os.path.join(dir_path, song.get_filename(ext, "clipped"))

    # download video only
    print(f"Getting Video Stream")
    vid_stream, found_res = get_highest_stream_resolution(yt.streams, target_res=target_res)
    print(f"Best Video Stream {vid_stream}")
    vid_path = vid_stream.download(output_path=dir_path, filename="video.mp4")

    # download audio only
    print(f"Getting Audio Stream")
    aud_stream = yt.streams.filter(only_audio=True, progressive=False).order_by("abr").last()
    print(f"Best Audio Stream {aud_stream}")
    aud_path = aud_stream.download(output_path=dir_path, filename="audio.mp4")

    print(f"{song.title} Streams Downloaded")
    # combine
    combine_audio_video(config, song, vid_path, aud_path, ext)
    os.remove(vid_path)
    os.remove(aud_path)
    return file_path


def scale_letterbox_video(scale: bool, letterbox: bool, target_res: str, vid_path: str, remove : bool=True):
    # https://superuser.com/questions/891145/ffmpeg-upscale-and-letterbox-a-video
    if not os.path.exists(vid_path):
        return
    vf_compiled = []
    scale_expr = r"scale=(iw*sar)*min({width}/(iw*sar)\,{height}/ih):ih*min({width}/(iw*sar)\,{height}/ih):flags=lanczos"
    pad_expr = r"pad={width}:{height}:({width}-iw*min({width}/iw\,{height}/ih))/2:({height}-ih*min({width}/iw\,{height}/ih))/2"
    path, ext = os.path.splitext(vid_path)
    file_path = f"{path}.scaled{ext}"
    print(f"{path} :: target_res {target_res} scale {scale} - letterbox {letterbox}")
    res_width, res_height = phgen.video_data.get_pixel_size(target_res)
    video = (
        ffmpeg.input(vid_path).video
    )
    audio = (
        ffmpeg.input(vid_path).audio
    )
    if scale:
        vf_compiled.append(scale_expr.format(width=res_width, height=res_height))
    if letterbox:
        vf_compiled.append(pad_expr.format(width=res_width, height=res_height))
    vf_text = ", ".join(vf_compiled)
    ffmpeg.output(audio, video, file_path, vf=vf_text).run(overwrite_output=True)
    if remove:
        os.remove(vid_path)
    return file_path


def combine_audio_video(config: PowerHourConfig, song: PowerHourSong, vid_path: str, aud_path: str, ext: str = "mp4"):
    # TODO Figure out how to upscale and pad in the same encoding, currently done seperately
    dir_path = config.get_dir_path()
    file_path = os.path.join(dir_path, song.get_filename(ext, "clipped"))
    video = ffmpeg.input(vid_path)
    audio = ffmpeg.input(aud_path)

    # non-mp4 stuff is broken as fuck fix me plz
    match ext:
        case "ts":
            # converting to Transport Stream as intermediary because it supports concat and mp4 does not
            # remove vcodec, format(f) and change path ending above if you want to switch to combine as mp4
            # ffmpeg -i file1.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts fileIntermediate1.ts
            ffmpeg.output(audio, video, file_path, vcodec="libx264", f="mpegts").run(overwrite_output=True)
        case _:  # also mp4
            ffmpeg.output(audio, video, file_path).run(overwrite_output=True)
    print(f"{song.title} ffmpeg combine_audio_video output complete")
    return file_path

def clip(config: PowerHourConfig, song: PowerHourSong, vid_path: str, ext: str = "mp4"):
    # TODO Figure out how to upscale and pad in the same encoding, currently done seperately
    dir_path = config.get_dir_path()
    file_path = os.path.join(dir_path, song.get_filename(ext, "clipped"))
    video = (ffmpeg.input(vid_path)
            .trim(start=song.start_time, end=song.end_time)
            .setpts('PTS-STARTPTS') # I have no fucking idea if this is necessary
        )
        
    # non-mp4 stuff is broken as fuck fix me plz
    match ext:
        case "ts":
            # converting to Transport Stream as intermediary because it supports concat and mp4 does not
            # remove vcodec, format(f) and change path ending above if you want to switch to combine as mp4
            # ffmpeg -i file1.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts fileIntermediate1.ts
            ffmpeg.output(video, file_path, vcodec="libx264", f="mpegts").run(overwrite_output=True)
        case _:  # also mp4
            ffmpeg.output(video, file_path).run(overwrite_output=True)
    print(f"{song.title} ffmpeg combine_audio_video output complete")
    return file_path


def process_song_effects(config: PowerHourConfig, song: PowerHourSong, num: int, vid_path: str,
                         ext: str = "mp4", add_text: bool = True, add_fade: bool = True, remove: bool = True):
    print(f"{add_text} {add_fade}")
    dir_path = config.get_dir_path()
    file_path = os.path.join(dir_path, song.get_filename(ext, "effects"))

    ffmpeg_input = ffmpeg.input(vid_path)
    # dynamic values determined by both song and config params
    title_start_time = config.title_start_time
    title_end_time = title_start_time + config.title_duration
    fade_out_start_time = (song.end_time - song.start_time) - config.fade_duration
    enable_expr = f'between(t,{title_start_time},{title_end_time})'
    song_num_str = str(num) if num != 60 else "60!"  # ╰(*°▽°*)╯ this case might need some thinking
    video = ffmpeg_input.video
    if add_text:
        # this syntax is fucking weird
        video = ffmpeg.drawtext(video,
                                text=song.artist.upper(),
                                x=song_title_pos.get_x_expr(),
                                y=song_title_pos.get_y_expr(),
                                enable=enable_expr,
                                fontfile=config.get_full_font_path(),
                                fontsize=config.artist_font_size,
                                fontcolor=config.font_color,
                                bordercolor=config.font_border_color,
                                borderw=config.font_border_width)
        video = ffmpeg.drawtext(video,
                                text=song.title,
                                x=song_title_pos.get_x_expr(),
                                y=song_title_pos.get_y_expr(config.artist_font_size * 1.5),
                                enable=enable_expr,
                                fontfile=config.get_full_font_path(),
                                fontsize=config.title_font_size,
                                fontcolor=config.font_color,
                                bordercolor=config.font_border_color,
                                borderw=config.font_border_width)
        video = ffmpeg.drawtext(video,
                                text=song_num_str,
                                x=song_number_pos.get_x_expr(),
                                y=song_number_pos.get_y_expr(),
                                fontfile=config.get_full_font_path(),
                                fontsize=config.number_font_size,
                                fontcolor=config.font_color,
                                bordercolor=config.font_border_color,
                                borderw=config.font_border_width)
    if add_fade:
        video = ffmpeg.filter(video, 'fade', type="in", duration=config.fade_duration)
        video = ffmpeg.filter(video, 'fade', type="out", start_time=fade_out_start_time, duration=config.fade_duration)

    audio = ffmpeg_input.audio
    if add_fade:
        audio = ffmpeg.filter(audio, 'afade', type="in", duration=config.fade_duration)
        audio = ffmpeg.filter(audio, 'afade', type="out", start_time=fade_out_start_time, duration=config.fade_duration)

    # non-mp4 stuff is broken as fuck fix me plz
    match ext:
        case "ts":
            # converting to Transport Stream as intermediary because it supports concat and mp4 does not
            # remove vcodec, format(f) and change path ending above if you want to switch to combine as mp4
            # ffmpeg -i file1.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts fileIntermediate1.ts
            ffmpeg.output(audio, video, file_path, vcodec="libx264", f="mpegts").run(overwrite_output=True)
        case _:  # also mp4
            ffmpeg.output(audio, video, file_path).run(overwrite_output=True)
    print(f"ffmpeg process_song_effects output complete")
    if remove:
        os.remove(vid_path)
    return file_path


def process_interstitial(config: PowerHourConfig, interstitial_path: str):
    dir_path = config.get_dir_path()
    output_path = os.path.join(dir_path, f"{interstitial_filename}_{config.project_name}.ts")

    metadata = ffmpeg.probe(interstitial_path)
    video_stream = next((stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None)
    duration = float(video_stream['duration'])
    fade_out_start_time = duration - config.fade_duration
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


def concat_power_hour(config: PowerHourConfig, interstitial_path: str, video_paths: list, song_limit: int = 0):
    interstitial_valid = os.path.exists(interstitial_path)
    dir_path = config.get_dir_path()
    output_path = os.path.join(dir_path, f"{config.project_name}_output.mp4")
    txt_path = 'tmp.txt'
    if 0 < song_limit < len(video_paths):
        video_paths = video_paths[:song_limit]
    with open(txt_path, 'w') as f:
        for video_path in video_paths:
            f.write(f"file {video_path}\n")
            if interstitial_valid:
                f.write(f"file {interstitial_path}\n")
    # ffmpeg -f concat -safe 0 -i tmp.txt -c copy output.mp4
    ffmpeg.input(txt_path, f='concat', safe='0').output(output_path, vcodec='libx264').run(overwrite_output=True)
    os.remove(txt_path)


def should_scale_letterbox(res: str, vid_path: str):
    # https://superuser.com/questions/891145/ffmpeg-upscale-and-letterbox-a-video
    if not os.path.exists(vid_path):
        return False, False
    metadata = ffmpeg.probe(vid_path)
    # 'display_aspect_ratio' : str '4:3'
    # 'r_frame_rate' : str '25/1'
    # 'width' : int 2400
    # 'height' : int 1800
    # 'codec_name' : str 'av1'
    video_stream = next((stream for stream in metadata['streams'] if stream['codec_type'] == 'video'), None)
    scale = True
    result = phgen.video_data.get_resolution(video_stream['width'], video_stream['height'])
    if phgen.video_data.get_resolution(video_stream['width'], video_stream['height']) == res:
        scale = False
    if "display_aspect_ratio" in video_stream:
        letterbox = True if video_stream['display_aspect_ratio'] != "16:9" else False
    else:
        letterbox = True
    return scale, letterbox


def get_highest_stream_resolution(streams: StreamQuery, target_res: str = ""):
    streams = streams.filter(adaptive=True).order_by("resolution")
    stream = streams.filter(subtype="mp4", resolution=target_res).first()
    if stream is not None:
        return stream, target_res
    else:
        stream = streams.last()
        return stream, stream.resolution
