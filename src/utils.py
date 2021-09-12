import platform, os, subprocess, fnmatch, shutil, requests, sys, zipfile, time

ffmpeg_download_link = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
ffmpeg_download_path = "%s/downloads/ffmpeg-release-essentials.zip" % os.getcwd()
ffmpeg_path = "%s/ffmpeg" % os.getcwd()
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

    print("Couldn't locate FFmpeg.")
    return False

def install_ffmpeg() -> None:
    global ffmpeg_installed
    global ffmpeg_downloaded
    
    if platform.system() == "Windows":
        if not os.path.exists("%s/ffmpeg" % os.getcwd()):
            os.mkdir("%s/ffmpeg" % os.getcwd())
            print("FFmpeg directory created.")
        
        if not os.path.exists("%s/downloads" % os.getcwd()):
            os.mkdir("%s/downloads" % os.getcwd())
            print("Downloads directory created.")
            
        if os.path.isfile("%s/ffmpeg.exe" % ffmpeg_path):
            ffmpeg_installed = True
            print("Found ffmpeg!")
        else:            
            with open(ffmpeg_download_path, "wb") as f:
                print("Downloading ffmpeg to %s" % ffmpeg_download_path)
                print("Please wait...")
                response = requests.get(ffmpeg_download_link, stream=True)
                total_length = response.headers.get('content-length')

                if total_length is None:
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    
                    for data in response.iter_content(chunk_size=4096):
                        dl += len(data)
                        f.write(data)
                        done = int(50 * dl / total_length)
                        sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                        sys.stdout.flush()
                    
            ffmpeg_downloaded = True
            print("\n")
            unzip_ffmpeg()

def unzip_ffmpeg() -> None:
    print("Unzipping ffmpeg contents...")    
    shutil.unpack_archive(ffmpeg_download_path, ffmpeg_path)
    print("Unzipped ffmpeg contents.")
    move_files()

def move_files() -> None:
    global ffmpeg_installed
    files = get_files()
    print("Moving files...")

    if files:
        for name in files:
            shutil.move(name, "%s/ffmpeg" % os.getcwd())

        ffmpeg_installed = True
        print("Moved files.")

def get_files() -> None:
    for path, dirlist, filelist in os.walk(os.getcwd() + "/ffmpeg"):
        for name in fnmatch.filter(filelist, "*.exe"):
            yield os.path.join(path, name)