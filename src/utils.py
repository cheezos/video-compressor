from datetime import datetime
import os

def log(msg) -> str:
    print('PVC: ' + str(msg))
    return msg

def pretty_time() -> str:
    return datetime.now().strftime("%H:%M:%S")

def raw_time() -> float:
    return datetime.now()

def list_videos(str) -> list:
    vids = str.split(';')
    log(f'Selected {len(vids)} videos.')
    return vids

def seconds_to_ffmpeg_readable(seconds) -> str:


    return str(seconds)

def remove_extension(video_path) -> str:
    split_slash = video_path.split('/')
    split_extension = os.path.splitext(split_slash[-1])
    return split_extension[0]

def get_extension(video_path) -> str:
    split_slash = video_path.split('/')
    split_extension = os.path.splitext(split_slash[-1])
    return split_extension[1]