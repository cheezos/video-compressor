# Created by asick
# https://github.com/asickwav/video-compressor
# Python 3.9.7 64-bit

import platform, os, subprocess, fnmatch, shutil, requests

ffmpeg_download_link = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
ffmpeg_download_path = "%s/downloads/ffmpeg-release-essentials.zip" % os.getcwd()
ffmpeg_path = "%s/ffmpeg" % os.getcwd()
ffmpeg_is_downloading = False
ffmpeg_downloaded = False
ffmpeg_installed = False

def validate_ffmpeg() -> bool:
    global ffmpeg_installed
    
    if not platform.system() == "Windows":
        p = subprocess.Popen("which ffmpeg", stdout=subprocess.PIPE, shell=True)
        result = p.stdout.readline()
        
        if result:
            ffmpeg_installed = True
            print("FFmpeg validated!")
            return True
    else:
        if os.path.exists(os.getcwd() + "/ffmpeg/ffmpeg.exe") and os.path.exists(os.getcwd() + "/ffmpeg/ffprobe.exe"):
            ffmpeg_installed = True
            print("FFmpeg validated!")
            return True

    print("Couldn't locate FFmpeg, will download.")
    install_ffmpeg()
    return False

def install_ffmpeg() -> None:
    global ffmpeg_installed
    global ffmpeg_downloaded
    global ffmpeg_is_downloading
    
    if platform.system() == "Windows":
        if not os.path.exists("%s/ffmpeg" % os.getcwd()):
            os.mkdir("%s/ffmpeg" % os.getcwd())
            print("FFmpeg directory created.")
        
        if not os.path.exists("%s/downloads" % os.getcwd()):
            os.mkdir("%s/downloads" % os.getcwd())
            print("Downloads directory created.")
            
        if os.path.isfile("%s/ffmpeg.exe" % ffmpeg_path):
            ffmpeg_installed = True
            print("Found FFmpeg.")
            print("Click Help to check what each setting does.\nReady.")
        else:
            ffmpeg_is_downloading = True
            
            with open(ffmpeg_download_path, "wb") as f:
                print("Downloading ffmpeg to %s" % ffmpeg_download_path)
                response = requests.get(ffmpeg_download_link, stream=True)
                total_length = response.headers.get('content-length')

                if total_length is None:
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    
                    for data in response.iter_content(chunk_size=1024):
                        dl += len(data)
                        f.write(data)
                        progress_percent = (dl / total_length) * 100
                        print("Downloading FFmpeg: %s/%s (%s)" % (round(dl), round(total_length), round(progress_percent)))
                    
            ffmpeg_downloaded = True
            ffmpeg_is_downloading = False
            print("\n")
            unzip_ffmpeg()

def unzip_ffmpeg() -> None:
    print("Unzipping ffmpeg contents...")    
    shutil.unpack_archive(ffmpeg_download_path, ffmpeg_path)
    print("Unzipped ffmpeg contents.")
    move_files()

def get_ffmpeg_path() -> str:
    if platform.system() == "Windows":
        return "%s/ffmpeg/ffmpeg.exe" % os.getcwd()
    else:
        return "ffmpeg"

def get_ffprobe_path() -> str:
    if platform.system() == "Windows":
        return "%s/ffmpeg/ffprobe.exe" % os.getcwd()
    else:
        return "ffprobe"

def move_files() -> None:
    global ffmpeg_installed
    files = get_files()
    print("Moving files...")

    if files:
        for name in files:
            shutil.move(name, "%s/ffmpeg" % os.getcwd())

        ffmpeg_installed = True
        print("Moved files.")
        print("Click Help to check what each setting does.\nReady.")

def get_files() -> None:
    for path, dirlist, filelist in os.walk(os.getcwd() + "/ffmpeg"):
        for name in fnmatch.filter(filelist, "*.exe"):
            yield os.path.join(path, name)

def list_videos(videos) -> list:
    if videos != "":
        return videos.split(';')
    else:
        return []

def calculate_video_bitrate(video, target_file_size, audio_bitrate) -> float:
    video_duration = get_video_duration(video)

    if video_duration:
        magic = round(((target_file_size * 8192.0) / (1.048576 * video_duration) - audio_bitrate))
        return magic
    else:
        return None

def get_video_duration(video) -> float:
    try:
        video = '"%s"' % video
        cmd = "%s -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s" % (get_ffprobe_path(), video)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        return float(proc.stdout.readline())
    except:
        print("Couldn't get video duration!")
        print("If you trimmed this video try different trim settings.")
        return None

def get_video_name(video) -> str:
    name_with_extension = os.path.basename(video)
    split = name_with_extension.split('.')
    just_name = name_with_extension.replace('.' + split[-1], '')
    return just_name

def get_video_extension(video) -> str:
    name_with_extension = os.path.basename(video)
    split = name_with_extension.split('.')
    just_extension = '.' + split[-1]
    return just_extension

def get_video_path(video) -> str:
    name_with_extension = os.path.basename(video)
    just_path = video.replace(name_with_extension, '')
    return just_path