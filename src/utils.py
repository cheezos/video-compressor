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
        name = get_name(vid)
        extension = get_extension(vid)
        path = vid.split(name)[0]
        vid_name_no_spaces = name.replace(' ', '-')
        new_vid = path + vid_name_no_spaces + extension
        os.rename(vid, new_vid)
        vids_new.append(new_vid)

    print('Renamed videos with spaces.')
    print(f'Selected {len(vids_new)} video(s).')
    return vids_new

def get_ffmpeg() -> str:
    ffmpeg = 'ffmpeg' if platform.system() == 'Linux' else os.getcwd() + '/FFmpeg/ffmpeg.exe'
    return ffmpeg

def get_ffprobe() -> str:
    ffprobe = 'ffprobe' if platform.system() == 'Linux' else os.getcwd() + '/FFmpeg/ffprobe.exe'
    return ffprobe

def validate_ffmpeg() -> bool:
    if not platform.system() == 'Windows':
        p = subprocess.Popen('which ffmpeg', stdout=subprocess.PIPE, shell=True)
        result = p.stdout.readline()
        if result: return True
    else:
        if os.path.exists(os.getcwd() + '/FFmpeg/ffmpeg.exe') and os.path.exists(os.getcwd() + '/FFmpeg/ffprobe.exe'):
            return True

    print("Couldn't locate FFmpeg.")
    return False

def install_ffmpeg() -> None:
        if platform.system() == 'Windows':
            if not os.path.exists(os.getcwd() + '/FFmpeg'):
                os.mkdir(os.getcwd() + '/FFmpeg')
                print('FFmpeg directory created.')
            
            print('Downloading FFmpeg, please wait...')
            dload.save_unzip('https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip', os.getcwd() + '/FFmpeg')
            print('FFmpeg downloaded.')

            files = get_files()

            if files:
                for name in files:
                    shutil.move(name, os.getcwd() + '/FFmpeg')

                print('Moved contents to FFmpeg directory.')
            
def get_files() -> None:
    for path, dirlist, filelist in os.walk(os.getcwd() + '/FFmpeg'):
        for name in fnmatch.filter(filelist, '*.exe'):
            yield os.path.join(path, name)

def get_video_duration(video) -> float:
    try:
        proc = subprocess.Popen(f'{get_ffprobe()} -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video}"', stdout=subprocess.PIPE, shell=True)
        return float(proc.stdout.readline())
    except:
        print('Invalid trim settings, check your video length.')
        return None

def calculate_video_bitrate(video, target_file_size, audio_bitrate) -> float:
    video_duration = get_video_duration(video)

    if video_duration:
        magic = ((target_file_size * 8192.0) / (1.048576 * video_duration) - audio_bitrate)
        return magic
    else:
        return None

def get_name(video) -> str:
    name_with_extension = os.path.basename(video)
    split = name_with_extension.split('.')
    just_name = name_with_extension.replace('.' + split[-1], '')
    return just_name

def get_extension(video) -> str:
    name_with_extension = os.path.basename(video)
    split = name_with_extension.split('.')
    just_extension = '.' + split[-1]
    return just_extension

def get_path(video) -> str:
    name_with_extension = os.path.basename(video)
    just_path = video.replace(name_with_extension, '')
    return just_path