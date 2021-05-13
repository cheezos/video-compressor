from datetime import datetime

import platform
import os
import subprocess
from sys import stdout

def pretty_time() -> str:
    return datetime.now().strftime("%H:%M:%S")

def raw_time() -> float:
    return datetime.now()

def list_videos(str) -> list:
    vids = str.split(';')
    print(f'Selected {len(vids)} video(s).')
    return vids

def get_ffmpeg() -> str:
    ffmpeg = 'ffmpeg' if platform.system() == 'Linux' else os.getcwd() + '\FFmpeg\ffmpeg.exe'
    return ffmpeg

def get_ffprobe() -> str:
    ffprobe = 'ffprobe' if platform.system() == 'Linux' else os.getcwd() + '\FFmpeg\ffprobe.exe'
    return ffprobe

def validate_ffmpeg() -> bool:
    if not platform.system() == 'Windows':
        p = subprocess.Popen('which ffmpeg', stdout=subprocess.PIPE, shell=True)
        result = p.stdout.readline()

        if result:
            print('Found FFmpeg.')
            return True
    else:
        if os.path.exists(os.getcwd() + '/FFmpeg/ffmpeg.exe') and os.path.exists(os.getcwd() + '/FFmpeg/ffprobe.exe'):
            print('Found FFmpeg.')
            return True
        else:
            # install_ffmpeg()
            pass

    print('Could not find FFmpeg.')
    return False

def get_video_duration(video) -> float:
    proc = subprocess.Popen(f'{get_ffprobe()} -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video}"', stdout=subprocess.PIPE, shell=True)
    return float(proc.stdout.readline())

def calculate_video_bitrate(video, target_file_size, audio_bitrate) -> float:
    video_duration = get_video_duration(video)
    magic = ((target_file_size * 8192.0) / (1.048576 * video_duration) - audio_bitrate)
    return magic

def remove_extension(video) -> str:
    split_slash = video.split('/')
    split_extension = os.path.splitext(split_slash[-1])
    return split_extension[0]

def get_extension(video) -> str:
    split_slash = video.split('/')
    split_extension = os.path.splitext(split_slash[-1])
    return split_extension[1]