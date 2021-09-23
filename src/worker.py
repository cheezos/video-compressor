from PyQt5.QtCore import QObject, pyqtSignal
import os, requests, shutil, fnmatch, subprocess

class Worker(QObject):
    signal_message = pyqtSignal(str, bool)
    signal_finished = pyqtSignal()
    
    def __init__(self, videos=[], file_size=8, remove_audio=False) -> None:
        QObject.__init__(self)
        self.download_link = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        self.download_path = "%s/downloads/ffmpeg-release-essentials.zip" % os.getcwd()
        self.ffmpeg_path = "%s/ffmpeg" % os.getcwd()
        
        self.target_file_size: float = float(file_size)
        self.remove_audio: bool = bool(remove_audio)
        self.audio_bitrate = 128
        self.fps = 30
        self.file_extension = "mp4"
        
        self.compressing: bool = False
        self.selected_videos: list = videos
        self.cur_video: str = ""
        self.cur_video_name: str = ""
        self.cur_video_path: str = ""
        self.cur_video_extension: str = ""
        self.cur_queue: int = 0
        self.cur_pass: int = 1
        self.proc: str = ""
    
    def install_ffmpeg(self) -> None:
        if not os.path.exists("%s/ffmpeg" % os.getcwd()):
            os.mkdir("%s/ffmpeg" % os.getcwd())
            self.signal_message.emit("FFmpeg directory created.", False)
        
        if not os.path.exists("%s/downloads" % os.getcwd()):
            os.mkdir("%s/downloads" % os.getcwd())
            self.signal_message.emit("Downloads directory created.", False)
            
        if not os.path.isfile("%s/ffmpeg.exe" % self.ffmpeg_path):      
            with open(self.download_path, "wb") as f:
                self.signal_message.emit("Downloading ffmpeg to %s" % self.download_path, True)
                response = requests.get(self.download_link, stream=True)
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
                        self.signal_message.emit("Downloading FFmpeg: %s/%s (%s%s)" % (round(dl), round(total_length), round(progress_percent), "%"), True)
            
            self.signal_message.emit("Unzipping contents...", True)
            shutil.unpack_archive(self.download_path, self.ffmpeg_path)
            files = self.get_files()
            self.signal_message.emit("Moving contents...", False)
            
            if files:
                for name in files:
                    shutil.move(name, "%s/ffmpeg" % os.getcwd())
            
            self.signal_message.emit("FFmpeg installed!", True)
            self.signal_finished.emit()
        
    def get_files(self) -> None:
        for path, dirlist, filelist in os.walk(os.getcwd() + "/ffmpeg"):
            for name in fnmatch.filter(filelist, "*.exe"):
                yield os.path.join(path, name)
    
    def compress(self) -> None:
        if not self.compressing:
            self.cur_video = self.selected_videos[self.cur_queue]
            
            input = '"%s"' % self.cur_video
            codec = "libx264"
            video_bitrate = self.calculate_video_bitrate(self.cur_video, self.target_file_size, self.audio_bitrate)
            audio_bitrate = "-b:a %sk" % self.audio_bitrate if not self.remove_audio else "-an"
            fps = "%s" % self.fps
            output = '"%s%s-compressed%s"' % (self.get_video_path(self.cur_video), self.get_video_name(self.cur_video), self.file_extension)
            
            pass_1 = "%s -i %s -y -c:v %s -b:v %sk -r %s -pass 1 -an -f mp4 TEMP" % (
                self.ffmpeg_path, input, codec, video_bitrate, fps
            )
            
            pass_2 = "%s -y -i %s -y -c:v %s -b:v %sk -r %s -pass 2 -c:a aac %s %s" % (
                self.ffmpeg_path, input, codec, video_bitrate, fps, audio_bitrate, output
            )
            
            if self.cur_pass == 1:
                self.proc = subprocess.Popen(pass_1, stdout=subprocess.PIPE)
            else:
                self.proc = subprocess.Popen(pass_2, stdout=subprocess.PIPE)
                
            self.compressing = True
            self.signal_message.emit("Compressing video %s/%s, Pass %s/2..." % (self.cur_queue + 1, len(self.selected_videos), self.cur_pass), True)
        
        while self.compressing:
            stdout, stderr = self.proc.communicate()

            if self.proc.returncode == 0:
                self.compressing = False
                
                if self.cur_pass == 1:
                    self.cur_pass = 2
                    self.compress()
                else:
                    self.signal_message.emit("Video %s/%s compressed!\n" % (self.cur_queue + 1, len(self.selected_videos)), False)
                    self.cur_pass = 1
                    
                    if (self.cur_queue + 1 < len(self.selected_videos)):
                        self.cur_queue += 1
                        self.compress()
                    else:
                        self.signal_message.emit('Job done!', True)
            else:
                self.compressing = False
                self.signal_message.emit("Compression failed, aborting...", False)
                self.abort()
    
    def calculate_video_bitrate(self, video, target_file_size, audio_bitrate) -> float:
        video_duration = self.get_video_duration(video)

        if video_duration:
            magic = round(((target_file_size * 8192.0) / (1.048576 * video_duration) - audio_bitrate))
            return magic
        else:
            return None

    def get_video_duration(self, video) -> float:
        try:
            video = '"%s"' % video
            cmd = "%s -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s" % (self.get_ffprobe_path(), video)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            return float(proc.stdout.readline())
        except:
            self.signal_message.emit("Couldn't get video duration!", False)
            return None

    def get_video_name(self, video) -> str:
        name_with_extension = os.path.basename(video)
        split = name_with_extension.split('.')
        just_name = name_with_extension.replace('.' + split[-1], '')
        return just_name

    def get_video_extension(self, video) -> str:
        name_with_extension = os.path.basename(video)
        split = name_with_extension.split('.')
        just_extension = '.' + split[-1]
        return just_extension

    def get_video_path(self, video) -> str:
        name_with_extension = os.path.basename(video)
        just_path = video.replace(name_with_extension, '')
        return just_path

    def get_ffmpeg_path(self) -> str:
        return "%s/ffmpeg/ffmpeg.exe" % os.getcwd()

    def get_ffprobe_path(self) -> str:
        return "%s/ffmpeg/ffprobe.exe" % os.getcwd()

    def list_videos(self, videos) -> list:
        if videos != "":
            return videos.split(';')
        else:
            return []