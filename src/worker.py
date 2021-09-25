# Created by asick
# https://github.com/asickwav/video-compressor
# Python 3.9.7 64-bit

from PyQt5.QtCore import QObject, pyqtSignal
import os, requests, shutil, fnmatch, subprocess

class Worker(QObject):
    signal_message = pyqtSignal(str, bool)
    signal_ffmpeg_install_completed = pyqtSignal()
    signal_compression_completed = pyqtSignal()
    
    def __init__(self, videos=[], file_size=8.0, remove_audio=False) -> None:
        QObject.__init__(self)
        
        # FFmpeg
        self.download_link: str = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        self.download_path: str = "%s/downloads/ffmpeg-release-essentials.zip" % os.getcwd()
        self.ffmpeg_path: str = "%s/ffmpeg" % os.getcwd()
        
        # Compression settings        
        self.target_file_size: float = float(file_size)
        self.remove_audio: bool = bool(remove_audio)
        self.audio_bitrate: int = 64
        self.video_bitrate: int
        
        # Internal
        self.compressing: bool = False
        self.selected_videos: list = videos
        self.cur_video: str = ""
        self.cur_video_name: str = ""
        self.cur_video_path: str = ""
        self.cur_video_extension: str = ""
        self.cur_queue: int = 0
        self.cur_pass: int = 1
        self.proc: subprocess.Popen
        self.input: str
        self.output: str
    
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
            
            self.signal_ffmpeg_install_completed.emit()
        
    def get_files(self) -> None:
        for path, dirlist, filelist in os.walk(os.getcwd() + "/ffmpeg"):
            for name in fnmatch.filter(filelist, "*.exe"):
                yield os.path.join(path, name)
    
    def pass_1(self) -> None:
        if self.remove_audio: self.audio_bitrate = 0
        self.cur_video = self.selected_videos[self.cur_queue]
        self.input = '"%s"' % self.cur_video
        self.video_bitrate = self.calculate_video_bitrate(self.cur_video, self.target_file_size, self.audio_bitrate)
        self.output = '"%s%s-compressed.mp4"' % (self.get_video_path(self.cur_video), self.get_video_name(self.cur_video))
        
        pass_1 = "%s -i %s -y -c:v libx264 -vf scale=720:trunc(ow/a/2)*2 -b:v %sk -pass 1 -an -f mp4 TEMP" % (
            self.get_ffmpeg_path(), self.input, self.video_bitrate
        )
        
        self.proc = subprocess.Popen(pass_1, stdout=subprocess.PIPE, shell=False)
        
    def pass_2(self) -> None:
        audio = "-b:a %sk" % self.audio_bitrate if not self.remove_audio else "-an"
        pass_2 = "%s -y -i %s -y -c:v libx264 -vf scale=720:trunc(ow/a/2)*2 -b:v %sk -pass 2 -c:a aac %s %s" % (
            self.get_ffmpeg_path(), self.input, self.video_bitrate, audio, self.output
        )
        
        self.proc = subprocess.Popen(pass_2, stdout=subprocess.PIPE, shell=False)
    
    def compress(self) -> None:
        if not self.compressing:
            if self.cur_pass == 1:
                self.pass_1()
            else:
                self.pass_2()
                
            self.compressing = True
            self.signal_message.emit("Compressing video %s/%s, Pass %s/2..." % (
                self.cur_queue + 1, len(self.selected_videos), self.cur_pass), False)
        
        while self.compressing:
            stdout, stderr = self.proc.communicate()

            if self.proc.returncode == 0:
                self.compressing = False
                
                if self.cur_pass == 1:
                    self.cur_pass = 2
                    self.compress()
                else:
                    self.signal_message.emit("Video %s/%s compressed!" % (
                        self.cur_queue + 1, len(self.selected_videos)), False)
                    
                    self.cur_pass = 1
                    
                    if (self.cur_queue + 1 < len(self.selected_videos)):
                        self.cur_queue += 1
                        self.compress()
                    else:
                        self.signal_message.emit('Job done!', False)
                        self.signal_compression_completed.emit()
            else:
                self.compressing = False
                self.signal_message.emit("Compression aborted!", False)
                self.signal_compression_completed.emit()
    
    def calculate_video_bitrate(self, video, target_file_size, audio_bitrate) -> float:
        video_duration = self.get_video_duration(video)

        if video_duration:
            magic = max(1.0, round(((target_file_size * 8192.0) / (1.048576 * video_duration) - audio_bitrate)))
            
            if magic <= 64.0:
                self.signal_message.emit(
                    "[WARNING] Calculated video bitrate is extremely low (%skbps)!\nIncrease your target file size for better quality." % magic, False)
            else:
                self.signal_message.emit("New video bitrate: %skbps" % magic, False)
            
            return magic
        else:
            return 1.0

    def get_video_duration(self, video) -> float:
        try:
            video = '"%s"' % video
            cmd = "%s -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 %s" % (self.get_ffprobe_path(), video)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            return float(proc.stdout.readline())
        except:
            self.signal_message.emit("[WARNING] Couldn't get video duration!", False)
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