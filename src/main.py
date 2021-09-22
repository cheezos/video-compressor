# Created by asick
# https://github.com/asickwav/video-compressor
# Python 3.9.7 64-bit

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QPushButton, QLabel, QGridLayout, QLineEdit
from PyQt5.QtGui import QIcon, QFont
import utils as Utils
import platform, os, subprocess, psutil, webbrowser, threading, sys

class Main(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # App info
        self.version: str = "v1.2.0"
        self.title: str = "Asick Video Compressor %s" % self.version
        self.author: str = "Asick"

        # Options
        self.res_w: int = 1280
        self.res_h: int = 720
        self.target_file_size: float = 8
        self.audio_bitrate: float = 128
        self.fps: int = 30
        self.file_extension: str = "mp4"
        self.trim_s: str = "00:00:45"
        self.trim_e: str = "00:00:15"
        self.enable_trim: bool = False
        self.remove_audio: bool = False
        self.use_h265: bool = False
        self.portrait_mode: bool = False

        # UI
        self.width: int = 480
        self.height: int = 480

        self.label_title: QLabel = QLabel("%s Video Compressor %s" % (self.author, self.version), self)
        self.label_title.setFont(QFont("Arial", 12))
        self.label_title.setFixedWidth(self.width)
        self.label_title.setFixedHeight(30)
        self.label_title.move(0, 10)
        self.label_title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label_title.setStyleSheet("QLabel {background-color: red;}")

        self.label_select_videos: QLabel = QLabel("Select Videos", self)
        self.label_select_videos.setFont(QFont("Arial", 10))
        self.label_select_videos.setFixedWidth(self.width)
        self.label_select_videos.setFixedHeight(30)
        self.label_select_videos.move(0, 60)
        self.label_select_videos.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label_select_videos.setStyleSheet("QLabel {background-color: red;}")

        self.button_select_videos: QPushButton = QPushButton("Browse", self)
        self.button_select_videos.setFont(QFont("Arial", 12))
        self.button_select_videos.setFixedWidth(round(self.width * 0.25))
        self.button_select_videos.setFixedHeight(30)
        self.button_select_videos.setToolTip("Select videos to compress.")
        self.button_select_videos.move(10, 90)
        self.button_select_videos.clicked.connect(self.select_videos)

        self.ledit_video_list: QLineEdit = QLineEdit(self)
        self.ledit_video_list.setFixedWidth(round((self.width * 0.75) - 20))
        self.ledit_video_list.setFixedHeight(30)
        self.ledit_video_list.setPlaceholderText("Browse and select videos to compress.")
        self.ledit_video_list.move(round((self.width / 4) + 10), 90)

        self.button_select_videos: QPushButton = QPushButton("Compress", self)
        self.button_select_videos.setFont(QFont("Arial", 12))
        self.button_select_videos.setFixedWidth(round(self.width * 0.25))
        self.button_select_videos.setFixedHeight(30)
        self.button_select_videos.setToolTip("Compress the selected videos.")
        self.button_select_videos.move(round((self.width * 0.5) - (self.width * 0.25)), 130)
        self.button_select_videos.clicked.connect(self.compress)

        # States
        self.compressing: bool = False
        self.trimming: bool = False
        self.trimmed: bool = False

        self.selected_videos: list = []
        self.cur_video: str = ""
        self.cur_video_name: str = ""
        self.cur_video_path: str = ""
        self.cur_video_extension: str = ""
        self.cur_queue: int = 0
        self.cur_pass: int = 1
        self.proc: str = ""
        self.ffmpeg_path: str = Utils.get_ffmpeg_path()
        
        self.init_UI()

    def init_UI(self) -> None:
        screen = QApplication.primaryScreen()
        w = screen.size().width()
        h = screen.size().height()
        pos_x = round((w / 2) - (self.width / 2))
        pos_y = round((h / 2) - (self.height / 2))

        self.setWindowTitle(self.title)
        self.setGeometry(pos_x, pos_y, self.width, self.height)
        self.setMinimumSize(self.width, self.height)
        self.setMaximumSize(self.width, self.height)
        self.show()
    
    def select_videos(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.videos, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "", "All Files (*);;Python Files (*.py)", options=options)
        self.ledit_video_list.setText(str(self.videos))

    def compress(self) -> None:
        if not self.compressing:
            self.cur_video = self.selected_videos[self.cur_queue]
            
            if self.trimmed:
                self.cur_video = self.cur_video_trimmed
                print("Using trimmed version: %s" % self.cur_video_trimmed)
            
            input = '"%s"' % self.cur_video
            codec = "libx265" if self.use_h265 else "libx264"
            video_bitrate = Utils.calculate_video_bitrate(self.cur_video, self.target_file_size, self.audio_bitrate)
            audio_bitrate = "-b:a %sk" % self.audio_bitrate if not self.remove_audio else "-an"
            fps = "%s" % self.fps
            resolution = "%s:%s" % (self.res_w, self.res_h)
            output = '"%s%s-compressed%s"' % (Utils.get_video_path(self.cur_video), Utils.get_video_name(self.cur_video), self.file_extension)
            
            pass_1 = "%s -i %s -y -c:v %s -b:v %sk -r %s -vf scale=%s -pass 1 -an -f mp4 TEMP" % (
                self.ffmpeg_path, input, codec, video_bitrate, fps, resolution
            )
            
            pass_2 = "%s -y -i %s -y -c:v %s -b:v %sk -r %s -vf scale=%s -pass 2 -c:a aac %s %s" % (
                self.ffmpeg_path, input, codec, video_bitrate, fps, resolution, audio_bitrate, output
            )
            
            if self.cur_pass == 1:
                self.proc = subprocess.Popen(pass_1, stdout=subprocess.PIPE)
            else:
                self.proc = subprocess.Popen(pass_2, stdout=subprocess.PIPE)
                
            self.compressing = True
            print("Compressing video %s/%s, Pass %s/2..." % (self.cur_queue + 1, len(self.selected_videos), self.cur_pass))
        
        while self.compressing:
            stdout, stderr = self.proc.communicate()

            if self.proc.returncode == 0:
                self.compressing = False
                
                if self.cur_pass == 1:
                    self.cur_pass = 2
                    self.compress()
                else:
                    print("Video %s/%s compressed!\n" % (self.cur_queue + 1, len(self.selected_videos)))
                    self.cur_pass = 1
                    
                    if (self.cur_queue + 1 < len(self.selected_videos)):
                        self.cur_queue += 1
                        self.compress()
                    else:
                        print('Job done!\n')
            else:
                self.compressing = False
                print("Compression failed, aborting...")
                self.abort()

if __name__ == "__main__":
    app = QApplication([])
    main = Main()
    app.exec_()