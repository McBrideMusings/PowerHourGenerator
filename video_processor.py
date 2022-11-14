import os
import ffmpeg
from pytube import YouTube, StreamQuery
from powerhour import PowerHourSong, PowerHourConfig

video_tmp_filename = "video.mp4"
audio_tmp_filename = "audio.mp3"

def download_song(config: PowerHourConfig, song: PowerHourSong):
    print(f"Starting Download {song.title} by {song.artist}")

    yt = YouTube(song.link)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = os.path.join(dir_path, config.output_path)
    file_path = os.path.join(dir_path, song.get_filename())
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    # download audio only
    astream = yt.streams.filter(only_audio=True, progressive=False).order_by("abr").last()
    print(f"Best Audio Stream {astream}")
    a_path = astream.download(output_path=dir_path, filename=audio_tmp_filename)
    #a_path = yt.streams.filter(abr="160kbps", progressive=False).first().download(output_path=dir_path, filename=audio_tmp_filename)
    audio = ffmpeg.input(a_path)

    # download audio only
    vstream = yt.streams.filter(only_video=True, progressive=False).order_by("resolution").last()
    print(f"Best Video Stream {vstream}")
    v_path = vstream.download(output_path=dir_path, filename=video_tmp_filename)
    #v_path = yt.streams.filter(res="1080p", progressive=False).first().download(output_path=dir_path,filename=video_tmp_filename)
    video = ffmpeg.input(v_path)

    end_time = song.start_time + 60
    fade_end_start_time = end_time - config.fade_duration
    vid = (
        video
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
    command = ffmpeg.output(vid, aud, file_path)
    # ffmpeg.output(audio, video, file_path).run(overwrite_output=True)cc
    command.run(overwrite_output=True)
    os.remove(v_path)
    os.remove(a_path)


def get_highest_resolution(stream : StreamQuery):
    return stream.filter(adaptive=True).order_by("resolution").last()


