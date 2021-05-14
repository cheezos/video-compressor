from datetime import datetime

import platform
import os
import subprocess
import dload
import fnmatch
import shutil

def pretty_time() -> str:
    return datetime.now().strftime("%H:%M:%S")

def raw_time() -> float:
    return datetime.now()

def list_videos(str) -> list:
    vids_old = str.split(';')
    vids_new = []

    for vid in vids_old:
        vid2 = vid.replace(' ', '-')
        os.rename(vid, vid2)
        vids_new.append(vid2)

    print('Renamed videos with spaces.')
    print(f'Selected {len(vids_new)} video(s).')
    return vids_new

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
        if os.path.exists(os.getcwd() + '\FFmpeg\ffmpeg.exe') and os.path.exists(os.getcwd() + '\FFmpeg\ffprobe.exe'):
            print('Found FFmpeg.')
            return True
        else:
            install_ffmpeg()

    print('Could not locate FFmpeg.')
    return False

def install_ffmpeg() -> None:
        if platform.system() == 'Windows':
            if not os.path.exists(os.getcwd() + '\FFmpeg'):
                os.mkdir(os.getcwd() + '\FFmpeg')
                print('FFmpeg directory created.')
            
            print('Downloading FFmpeg, please wait...')
            dload.save_unzip('https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip', os.getcwd() + '\FFmpeg')
            print('FFmpeg downloaded.')

            files = get_files()

            if files:
                for name in files:
                    shutil.move(name, os.getcwd() + '\FFmpeg')

                print('Moved FFmpeg contents.')
            
def get_files() -> None:
    for path, dirlist, filelist in os.walk(os.getcwd() + '\FFmpeg'):
        for name in fnmatch.filter(filelist, '*.exe'):
            yield os.path.join(path, name)

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