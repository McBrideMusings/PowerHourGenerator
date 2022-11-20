import os
import ffmpeg
from pytube import YouTube, StreamQuery
from powerhour import PowerHourSong, PowerHourConfig

video_tmp_filename = "video.mp4"
audio_tmp_filename = "audio.mp3"

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


def process_media(config: PowerHourConfig, song: PowerHourSong, vid_path: str, aud_path: str):
    dir_path, file_path = get_paths(config, song)
    audio = ffmpeg.input(aud_path)
    video = ffmpeg.input(vid_path)
    end_time = song.start_time + 60
    text_start_time = song.start_time + 2
    text_start_fade_time = song.start_time + 5
    text_end_time = text_start_time + 5
    fade_end_start_time = end_time - config.fade_duration
    #'
    vid = (
        video
        .drawtext(text="No Doubt",x=640,y=360, fontsize=64, fontcolor='white',enable=f'between(t,{text_start_time},{text_end_time})')
        .trim(start=song.start_time, end=end_time)
        .filter('fade', type="in", start_time=song.start_time, duration=config.fade_duration)
        .filter('fade', type="out", start_time=fade_end_start_time, duration=config.fade_duration)
        .setpts('PTS-STARTPTS')
    )
    aud = (
        audio
        .filter_('atrim', start=song.start_time, end=end_time)
        .filter('afade', type="in", start_time=song.start_time, duration=config.fade_duration)
        .filter('afade', type="out", start_time=fade_end_start_time, duration=config.fade_duration)
        .filter_('asetpts', 'PTS-STARTPTS')
    )
    print("outputting")
    command = ffmpeg.output(vid, aud, file_path)
    # ffmpeg.output(audio, video, file_path).run(overwrite_output=True)cc
    command.run(overwrite_output=True)
    os.remove(vid_path)
    os.remove(aud_path)


def get_dir_path(config: PowerHourConfig):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.join(dir_path, config.output_path)
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


def get_highest_resolution(stream : StreamQuery):
    return stream.filter(adaptive=True).order_by("resolution").last()


