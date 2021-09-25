# Created by asick
# https://github.com/asickwav/video-compressor
# Python 3.9.7 64-bit

from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import QApplication, QFileDialog, QPushButton, QLabel, QLineEdit, QCheckBox, QTextEdit, QMainWindow
from PyQt5.QtGui import QFont, QTextCursor, QIcon
from configparser import ConfigParser
import os, psutil, webbrowser, time, json
from worker import Worker

class Main(QMainWindow):
    def __init__(self, parent=None) -> None:
        super(Main, self).__init__(parent)

        # App info
        self.version: str = "v1.2.0"
        self.title: str = "Asick Video Compressor %s" % self.version
        self.author: str = "Asick"

        # FFmpeg
        self.ffmpeg_path: str = "%s/ffmpeg" % os.getcwd()
        self.ffmpeg_installed: bool = False

        # Video Options
        self.config: ConfigParser = ConfigParser()
        self.selected_videos: list = []
        self.target_file_size: float = 20.0
        self.remove_audio: bool = False

        # UI
        self.width: int = 400
        self.height: int = 430

        # Title
        self.label_title: QLabel = QLabel("%s Video Compressor %s" % (self.author, self.version), self)
        self.label_title.setFont(QFont("Arial", 12))
        self.label_title.setFixedWidth(self.width)
        self.label_title.setFixedHeight(30)
        self.label_title.move(0, 10)
        self.label_title.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.label_select_videos: QLabel = QLabel("github.com/asickwav/video-compressor", self) 
        self.label_select_videos.setFont(QFont("Arial", 8))
        self.label_select_videos.setFixedWidth(self.width)
        self.label_select_videos.setFixedHeight(30)
        self.label_select_videos.move(0, 40)
        self.label_select_videos.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        # Select Videos
        self.button_select_videos: QPushButton = QPushButton("Browse", self)
        self.button_select_videos.setFont(QFont("Arial", 10))
        self.button_select_videos.setFixedWidth(round(self.width * 0.33 - 5))
        self.button_select_videos.setFixedHeight(30)
        self.button_select_videos.setToolTip("Select videos to compress.")
        self.button_select_videos.move(10, 90)
        self.button_select_videos.clicked.connect(self.select_videos)

        self.ledit_video_list: QLineEdit = QLineEdit(self)
        self.ledit_video_list.setFixedWidth(round(self.width * 0.66 - 15))
        self.ledit_video_list.setFixedHeight(30)
        self.ledit_video_list.setPlaceholderText("Browse and select videos to compress.")
        self.ledit_video_list.move(round(self.width * 0.33 + 10), 90)

        # Target File Size
        self.label_file_size: QLabel = QLabel("Target File Size", self)
        self.label_file_size.setFont(QFont("Arial", 10))
        self.label_file_size.setFixedWidth(round(self.width * 0.33 - 5))
        self.label_file_size.setFixedHeight(30)
        self.label_file_size.setToolTip("Set the file size to compress your videos to in megabytes.")
        self.label_file_size.move(10, 130)
        self.label_file_size.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.ledit_file_size: QLineEdit = QLineEdit(self)
        self.ledit_file_size.setFixedWidth(50)
        self.ledit_file_size.setFixedHeight(30)
        self.ledit_file_size.setText("8")
        self.ledit_file_size.move(round(self.width * 0.33 + 10), 130)

        self.label_mb: QLabel = QLabel("MB", self)
        self.label_mb.setFont(QFont("Arial", 10))
        self.label_mb.setFixedWidth(50)
        self.label_mb.setFixedHeight(30)
        self.label_mb.setToolTip("Set the file size to compress your videos to in megabytes.")
        self.label_mb.move(round(self.width * 0.33 + 70), 130)

        # Remove Audio
        self.label_remove_audio: QLabel = QLabel("Remove Audio", self)
        self.label_remove_audio.setFont(QFont("Arial", 10))
        self.label_remove_audio.setFixedWidth(round(self.width * 0.33 - 5))
        self.label_remove_audio.setFixedHeight(30)
        self.label_remove_audio.setToolTip("Remove audio from your videos.")
        self.label_remove_audio.move(10, 170)
        self.label_remove_audio.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.cb_remove_audio: QCheckBox = QCheckBox(self)
        self.cb_remove_audio.setFixedWidth(50)
        self.cb_remove_audio.setFixedHeight(30)
        self.cb_remove_audio.move(round(self.width * 0.33 + 10), 170)

        # Output
        self.output: QTextEdit = QTextEdit(self)
        self.output.setFixedWidth(self.width - 20)
        self.output.setFixedHeight(170)
        self.output.move(10, 210)

        # Buttons
        self.button_select_videos: QPushButton = QPushButton("Compress", self)
        self.button_select_videos.setFont(QFont("Arial", 10))
        self.button_select_videos.setFixedWidth(round(self.width * 0.25))
        self.button_select_videos.setFixedHeight(30)
        self.button_select_videos.setToolTip("Compress the selected videos.")
        self.button_select_videos.move(0, self.height - 40)
        self.button_select_videos.clicked.connect(self.start)

        self.button_abort: QPushButton = QPushButton("Abort", self)
        self.button_abort.setFont(QFont("Arial", 10))
        self.button_abort.setFixedWidth(round(self.width * 0.25))
        self.button_abort.setFixedHeight(30)
        self.button_abort.setToolTip("Abort the compression process.")
        self.button_abort.move(round(self.width * 0.25), self.height - 40)
        self.button_abort.clicked.connect(self.abort)

        self.button_support: QPushButton = QPushButton("Support Me", self)
        self.button_support.setFont(QFont("Arial", 10))
        self.button_support.setFixedWidth(round(self.width * 0.25))
        self.button_support.setFixedHeight(30)
        self.button_support.setToolTip("Open Ko-Fi page.")
        self.button_support.move(round(self.width * 0.25) * 2, self.height - 40)
        self.button_support.clicked.connect(self.support)

        self.button_github: QPushButton = QPushButton("Github", self)
        self.button_github.setFont(QFont("Arial", 10))
        self.button_github.setFixedWidth(round(self.width * 0.25))
        self.button_github.setFixedHeight(30)
        self.button_github.setToolTip("Open Github page.")
        self.button_github.move(round(self.width * 0.25) * 3, self.height - 40)
        self.button_github.clicked.connect(self.support)

        # States
        self.compressing: bool = False

        # Internal
        self.thread: QThread
        self.worker: Worker
        
        # Init
        self.init_UI()
        self.init_config()
        self.init_ffmpeg()
        
    def init_config(self) -> None:
        self.config.read(os.getcwd() + "/config.ini")
        
        if os.path.exists(os.getcwd() + "/config.ini"):
            video_list = self.config.get("Options", "last_video_list").split(",")
            
            if video_list[0] == "":
                self.selected_videos.clear()
            else:
                self.selected_videos = video_list
                print(self.selected_videos)
                self.ledit_video_list.setText(str(self.selected_videos))
                
            self.target_file_size = self.config.getfloat("Options", "target_file_Size")
            self.remove_audio = self.config.getboolean("Options", "remove_audio")
            
            self.ledit_file_size.setText(str(self.target_file_size))
            self.cb_remove_audio.setChecked(self.remove_audio)
            
            self.print_console("Loaded config.")
        else:
            self.config.add_section("Options")
            self.config.set("Options", "last_video_list", self.list_to_string(self.selected_videos))
            self.config.set("Options", "target_file_size", str(self.target_file_size))
            self.config.set("Options", "remove_audio", str(self.remove_audio))
            
            with open(os.getcwd() + "/config.ini", "w") as config:
                self.config.write(config)

            config.close()
            self.init_config()
    
    def save_config(self) -> None:
        self.target_file_size = self.ledit_file_size.text()
        self.remove_audio = self.cb_remove_audio.isChecked()
                
        self.config.set("Options", "last_video_list", self.list_to_string(self.selected_videos))
        self.config.set("Options", "target_file_size", str(self.target_file_size))
        self.config.set("Options", "remove_audio", str(self.remove_audio))
        
        with open(os.getcwd() + "/config.ini", "w") as config:
            self.config.write(config)

        config.close()
        self.print_console("Config saved.")

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
    
    def init_ffmpeg(self) -> None:  
        if os.path.exists(os.getcwd() + "/ffmpeg/ffmpeg.exe") and os.path.exists(os.getcwd() + "/ffmpeg/ffprobe.exe"):
            self.ffmpeg_installed = True
        else:
            self.compression_completed()
            self.thread = QThread(parent=self)
            self.worker = Worker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.install_ffmpeg)
            self.worker.signal_message.connect(self.print_console)
            self.worker.signal_ffmpeg_install_completed.connect(self.ffmpeg_install_completed)
            self.thread.start()
            
    def select_videos(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.selected_videos, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "", "All Files (*);;Python Files (*.py)", options=options)
        self.ledit_video_list.setText(str(self.selected_videos))
        print(self.selected_videos)

    def start(self) -> None:
        if not self.compressing:
            if len(self.selected_videos) > 0:
                if not self.ffmpeg_installed:
                    self.print_console("Please wait for FFmpeg to finish installing.")
                else:
                    self.target_file_size = self.ledit_file_size.text()
                    self.remove_audio = self.cb_remove_audio.isChecked()
                    self.compression_completed()
                    self.thread = QThread(parent=self)
                    self.worker = Worker(self.selected_videos, self.target_file_size, self.remove_audio)
                    self.worker.moveToThread(self.thread)
                    self.thread.started.connect(self.worker.compress)
                    self.worker.signal_message.connect(self.print_console)
                    self.worker.signal_compression_completed.connect(self.compression_completed)
                    self.thread.start()
                    
                    self.compressing = True
            else:
                self.print_console("No videos selected!")
        else:
            self.print_console("Compression started, click Abort to stop.")

    def abort(self) -> None:
        if not self.compressing: return
        
        for proc in psutil.process_iter():
            if "ffmpeg" in proc.name():
                p = psutil.Process(proc.pid)
                p.kill()

                self.compressing = False
        
        self.compression_completed()
        self.cleanup()

    def support(self) -> None:
        webbrowser.open("https://ko-fi.com/V7V82NKB5")

    def github(self) -> None:
        webbrowser.open("https://github.com/asickwav/video-compressor")
    
    def ffmpeg_install_completed(self) -> None:
        self.kill_thread()
        
        if os.path.exists(os.getcwd() + "/ffmpeg/ffmpeg.exe") and os.path.exists(os.getcwd() + "/ffmpeg/ffprobe.exe"):
            self.ffmpeg_installed = True
            self.print_console("FFmpeg installed!")
        else:
            self.init_ffmpeg()

    def compression_completed(self) -> None:
        self.kill_thread()
        self.compressing = False
        self.cleanup()
    
    def kill_thread(self) -> None:
        if self.thread is QThread:
            if self.thread.isRunning():
                self.thread.quit()
                time.sleep(1)
                self.thread = None
    
    def closeEvent(self, event) -> None:
        self.save_config()
        self.abort()
        event.accept()
    
    def list_to_string(self, list_to_parse) -> str:
        s = ""
        index = 1
        
        for e in list_to_parse:
            if index != len(list_to_parse):
                s += "%s," % e
            else:
                s += "%s" % e
            
            index += 1
            
        return s

    def cleanup(self) -> None:
        try:
            os.remove("TEMP")
            os.remove("ffmpeg2pass-0.log")
            os.remove("ffmpeg2pass-0.log.mbtree")
            self.print_console("Cleaned up temp files.")
        except:
            pass
    
    def print_console(self, message, overwrite_all=False) -> None:
        if overwrite_all:
            self.output.setText("%s\n" % message)
        else:
            self.output.setText(self.output.toPlainText() + "%s\n" % message)
            
        self.output.moveCursor(QTextCursor.End)
        print(message)

if __name__ == "__main__":
    app = QApplication([])
    app.setWindowIcon(QIcon("icon.ico"))
    main = Main()
    app.exec_()