import os
import subprocess
import psutil
import src.globals as g
from math import floor


def get_video_length(file_path):
    VIDEO = "%s" % file_path
    CMD = f'"{g.ffprobe_path}" -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{file_path}"'
    PROCESS = subprocess.Popen(CMD, stdout=subprocess.PIPE, shell=True)
    LENGTH = float(PROCESS.stdout.readline())
    print(f"Video duration: {LENGTH}")
    return LENGTH


def get_video_bitrate(file_path, target_file_size):
    VIDEO_LENGTH = get_video_length(file_path)
    MAGIC = max(
        1.0,
        floor(((target_file_size * 8192.0) / (1.048576 * VIDEO_LENGTH) - 128)),
    )
    return MAGIC


def clean():
    try:
        os.remove(os.path.join(g.dir_root, "TEMP"))
        os.remove(os.path.join(g.dir_root, "ffmpeg2pass-0.log"))
        os.remove(os.path.join(g.dir_root, "ffmpeg2pass-0.log.mbtree"))
    except:
        print("No temporary files to remove")


def kill_ffmpeg():
    for PROC in psutil.process_iter():
        if "ffmpeg" in PROC.name():
            PROC.kill()
