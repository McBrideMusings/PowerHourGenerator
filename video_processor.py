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
    print(f"Getting Audio Stream")
    astream = yt.streams.filter(only_audio=True, progressive=False).order_by("abr").last()
    print(f"Best Audio Stream {astream}")
    a_path = astream.download(output_path=dir_path, filename=audio_tmp_filename)
    #a_path = yt.streams.filter(abr="160kbps", progressive=False).first().download(output_path=dir_path, filename=audio_tmp_filename)
    audio = ffmpeg.input(a_path)

    # download video only
    print(f"Getting Video Stream")
    vstream = yt.streams.filter(only_video=True, progressive=False).order_by("resolution").last()
    print(f"Best Video Stream {vstream}")
    v_path = vstream.download(output_path=dir_path, filename=video_tmp_filename)
    #v_path = yt.streams.filter(res="1080p", progressive=False).first().download(output_path=dir_path,filename=video_tmp_filename)
    video = ffmpeg.input(v_path)
    end_time = song.start_time + 60
    text_start_time = song.start_time + 5
    text_start_fade_time = song.start_time + 5
    text_end_time = song.start_time + 6
    fade_end_start_time = end_time - config.fade_duration

    DS = 1.0  # display start
    DE = 10.0  # display end
    FID = 1.5  # fade in duration
    FOD = 5  # fade out duration
    text_expr = r"ff0000%{eif\\\\: clip(255*(1*between(t\\, $DS + $FID\\, $DE - $FOD) + ((t - $DS)/$FID)*between(t\\, $DS\\, $DS + $FID) + (-(t - $DE)/$FOD)*between(t\\, $DE - $FOD\\, $DE) )\\, 0\\, 255) \\\\: x\\\\: 2 }"
    text_expr.replace("$DS", str(DS))
    text_expr.replace("$DE", str(DE))
    text_expr.replace("$FID", str(FID))
    text_expr.replace("$FOD", str(FID))
    print(text_expr)
    vid = (
        video

        .trim(start=song.start_time, end=end_time)
        .filter('fade', type="in", start_time=song.start_time, duration=config.fade_duration)
        .filter('fade', type="out", start_time=fade_end_start_time, duration=config.fade_duration)
        .setpts('PTS-STARTPTS')
        .drawtext(text="Drake", x="10", y="h-th-10", fontsize=24, fontcolor="white", fontcolor_expr=text_expr)
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


