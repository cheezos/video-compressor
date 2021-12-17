# Created by Big Slime
# https://github.com/big-slime/video-compressor
# Python 3.9.7 64-bit

from PyQt5.QtCore import QThread, Qt
from PyQt5.QtWidgets import (
    QApplication,  
    QFileDialog,
    QPushButton,
    QLabel,
    QLineEdit,
    QCheckBox,
    QTextEdit,
    QMainWindow,
)
from PyQt5.QtGui import QFont, QTextCursor, QIcon
from configparser import ConfigParser
import os, psutil, webbrowser, time
from worker import Worker


class Main(QMainWindow):
    def __init__(self) -> None:
        super(Main, self).__init__()

        # Icon
        icon_path: str = f"{os.getcwd()}/icon.ico"
        self.setWindowIcon(QIcon(icon_path))

        # App info
        self.version: str = "v1.2.3"
        self.title: str = f"Big Slime Video Compressor {self.version}"
        self.author: str = "Big Slime"

        # Video Options
        self.config: ConfigParser = ConfigParser()
        self.selected_videos: list[str] = []
        self.target_file_size: float = 8.0
        self.remove_audio: bool = False
        self.support_link: str = "https://ko-fi.com/bigslime"
        self.github_link: str = "https://github.com/big-slime/video-compressor"

        # States
        self.compressing: bool = False
        self.ffmpeg_installed: bool = False

        # Internal
        self.thread: QThread
        self.worker: Worker

        # UI
        self.width: int = 400
        self.height: int = 350

        # Select Videos
        self.btn_select_videos: QPushButton = QPushButton("Browse", self)
        self.btn_select_videos.setFont(QFont("Arial", 10))
        self.btn_select_videos.setFixedWidth(int(self.width * 0.33 - 5))
        self.btn_select_videos.setFixedHeight(30)
        self.btn_select_videos.setToolTip("Select videos to compress.")
        self.btn_select_videos.move(10, 10)
        self.btn_select_videos.clicked.connect(self.select_videos)

        self.le_video_list: QLineEdit = QLineEdit(self)
        self.le_video_list.setFixedWidth(int(self.width * 0.66 - 15))
        self.le_video_list.setFixedHeight(30)
        self.le_video_list.setPlaceholderText("Browse and select videos to compress.")
        self.le_video_list.move(int(self.width * 0.33 + 10), 10)

        # Target File Size
        self.label_file_size: QLabel = QLabel("Target File Size", self)
        self.label_file_size.setFont(QFont("Arial", 10))
        self.label_file_size.setFixedWidth(int(self.width * 0.33 - 5))
        self.label_file_size.setFixedHeight(30)
        self.label_file_size.setToolTip(
            "Set the file size to compress your videos to in megabytes."
        )
        
        self.label_file_size.move(10, 50)
        self.label_file_size.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.le_file_size: QLineEdit = QLineEdit(self)
        self.le_file_size.setFixedWidth(50)
        self.le_file_size.setFixedHeight(30)
        self.le_file_size.setText("8")
        self.le_file_size.move(int(self.width * 0.33 + 10), 50)

        self.label_mb: QLabel = QLabel("MB", self)
        self.label_mb.setFont(QFont("Arial", 10))
        self.label_mb.setFixedWidth(50)
        self.label_mb.setFixedHeight(30)
        self.label_mb.setToolTip(
            "Set the file size to compress your videos to in megabytes."
        )
        self.label_mb.move(int(self.width * 0.33 + 70), 50)

        # Remove Audio
        self.label_remove_audio: QLabel = QLabel("Remove Audio", self)
        self.label_remove_audio.setFont(QFont("Arial", 10))
        self.label_remove_audio.setFixedWidth(int(self.width * 0.33 - 5))
        self.label_remove_audio.setFixedHeight(30)
        self.label_remove_audio.setToolTip("Remove audio from your videos.")
        self.label_remove_audio.move(10, 90)
        self.label_remove_audio.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.cb_remove_audio: QCheckBox = QCheckBox(self)
        self.cb_remove_audio.setFixedWidth(50)
        self.cb_remove_audio.setFixedHeight(30)
        self.cb_remove_audio.move(int(self.width * 0.33 + 10), 90)

        # Output
        self.output: QTextEdit = QTextEdit(self)
        self.output.setFixedWidth(self.width - 20)
        self.output.setFixedHeight(170)
        self.output.move(10, 130)

        # Buttons
        self.btn_select_videos: QPushButton = QPushButton("Compress", self)
        self.btn_select_videos.setFont(QFont("Arial", 8))
        self.btn_select_videos.setFixedWidth(int(self.width * 0.25) - 5)
        self.btn_select_videos.setFixedHeight(30)
        self.btn_select_videos.setToolTip("Compress the selected videos.")
        self.btn_select_videos.move(10, self.height - 40)
        self.btn_select_videos.clicked.connect(self.start)

        self.btn_abort: QPushButton = QPushButton("Abort", self)
        self.btn_abort.setFont(QFont("Arial", 8))
        self.btn_abort.setFixedWidth(int(self.width * 0.25) - 5)
        self.btn_abort.setFixedHeight(30)
        self.btn_abort.setToolTip("Abort the compression process.")
        self.btn_abort.move(int(self.width * 0.25) + 5, self.height - 40)
        self.btn_abort.clicked.connect(self.abort)

        self.btn_support: QPushButton = QPushButton("Support Me", self)
        self.btn_support.setFont(QFont("Arial", 8))
        self.btn_support.setFixedWidth(int(self.width * 0.25) - 5)
        self.btn_support.setFixedHeight(30)
        self.btn_support.setToolTip("Open Ko-Fi page.")
        self.btn_support.move(int(self.width * 0.5), self.height - 40)
        self.btn_support.clicked.connect(self.support)

        self.btn_github: QPushButton = QPushButton("Github", self)
        self.btn_github.setFont(QFont("Arial", 8))
        self.btn_github.setFixedWidth(int(self.width * 0.25) - 5)
        self.btn_github.setFixedHeight(30)
        self.btn_github.setToolTip("Open Github page.")
        self.btn_github.move(int(self.width * 0.75) - 5, self.height - 40)
        self.btn_github.clicked.connect(self.github)

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
                self.le_video_list.setText(str(self.selected_videos))

            self.target_file_size = self.config.getfloat("Options", "target_file_Size")
            self.remove_audio = self.config.getboolean("Options", "remove_audio")
            self.le_file_size.setText(str(self.target_file_size))
            self.cb_remove_audio.setChecked(self.remove_audio)
            self.print_console("Loaded config.")
        else:
            self.config.add_section("Options")
            self.set_config()

            with open(f"{os.getcwd()}/config.ini", "w") as config:
                self.config.write(config)

            config.close()
            self.init_config()

    def save_config(self) -> None:
        self.target_file_size = self.le_file_size.text()
        self.remove_audio = self.cb_remove_audio.isChecked()
        self.set_config()

        with open(f"{os.getcwd()}/config.ini", "w") as config:
            self.config.write(config)

        config.close()
        self.print_console("Config saved.")

    def set_config(self) -> None:
        self.config.set(
            "Options", "last_video_list", self.list_to_string(self.selected_videos)
        )

        self.config.set("Options", "target_file_size", str(self.target_file_size))
        self.config.set("Options", "remove_audio", str(self.remove_audio))

    def init_UI(self) -> None:
        screen: QApplication = QApplication.primaryScreen()
        w: int = screen.size().width()
        h: int = screen.size().height()
        pos_x: int = int((w / 2) - (self.width / 2))
        pos_y: int = int((h / 2) - (self.height / 2))

        self.setWindowTitle(self.title)
        self.setGeometry(pos_x, pos_y, self.width, self.height)
        self.setMinimumSize(self.width, self.height)
        self.setMaximumSize(self.width, self.height)
        self.show()

    def init_ffmpeg(self) -> None:
        if os.path.exists(os.getcwd() + "/ffmpeg/ffmpeg.exe") and os.path.exists(
            os.getcwd() + "/ffmpeg/ffprobe.exe"
        ):
            self.ffmpeg_installed = True
        else:
            self.compression_completed()
            self.thread = QThread(parent=self)
            self.worker = Worker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.install_ffmpeg)
            self.worker.signal_message.connect(self.print_console)
            self.worker.signal_ffmpeg_install_completed.connect(
                self.ffmpeg_install_completed
            )
            self.thread.start()

    def select_videos(self) -> None:
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.selected_videos, _ = QFileDialog.getOpenFileNames(
            self,
            "QFileDialog.getOpenFileNames()",
            "",
            "All Files (*);;Python Files (*.py)",
            options=options,
        )
        self.le_video_list.setText(str(self.selected_videos))

    def start(self) -> None:
        if not self.compressing:
            if len(self.selected_videos) > 0:
                if not self.ffmpeg_installed:
                    self.print_console("Please wait for FFmpeg to finish installing.")
                else:
                    self.target_file_size = float(self.le_file_size.text())
                    self.remove_audio = self.cb_remove_audio.isChecked()
                    self.compression_completed()
                    self.thread = QThread(parent=self)
                    self.worker = Worker(
                        selected_videos=self.selected_videos,
                        target_file_size=self.target_file_size,
                        remove_audio=self.remove_audio,
                    )
                    self.worker.moveToThread(self.thread)
                    self.thread.started.connect(self.worker.compress)
                    self.worker.signal_message.connect(self.print_console)
                    self.worker.signal_compression_completed.connect(
                        self.compression_completed
                    )
                    self.thread.start()
                    self.compressing = True
            else:
                self.print_console("No videos selected!")
        else:
            self.print_console("Compression started, click Abort to stop.")

    def abort(self) -> None:
        if not self.compressing:
            return
        for proc in psutil.process_iter():
            if "ffmpeg" in proc.name():
                p = psutil.Process(proc.pid)
                p.kill()

                self.compressing = False

        self.compression_completed()
        self.cleanup()

    def support(self) -> None:
        webbrowser.open(self.support_link)

    def github(self) -> None:
        webbrowser.open(self.github_link)

    def ffmpeg_install_completed(self) -> None:
        self.kill_thread()
        if os.path.exists(os.getcwd() + "/ffmpeg/ffmpeg.exe") and os.path.exists(
            os.getcwd() + "/ffmpeg/ffprobe.exe"
        ):
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
        self.kill_thread()
        self.cleanup()
        self.save_config()
        event.accept()

    def list_to_string(self, list_to_parse) -> str:
        s = ""
        index = 1
        for e in list_to_parse:
            if index != len(list_to_parse):
                s += f"{e},"
            else:
                s += f"{e}"

            index += 1

        return s

    def cleanup(self) -> None:
        junk: list[str] = [
            "TEMP",
            "ffmpeg2pass-0.log",
            "ffmpeg2pass-0.log.mbtree",
        ]

        for f in junk:
            if os.path.isfile(f):
                os.remove(f)

        self.print_console("Cleaned up logs and temporary files.")

    def print_console(self, message, overwrite_all=False) -> None:
        if overwrite_all:
            self.output.setText(f"{message}\n")
        else:
            self.output.setText(self.output.toPlainText() + f"{message}\n")

        self.output.moveCursor(QTextCursor.End)
        print(message)


if __name__ == "__main__":
    app = QApplication([])
    main = Main()
    app.exec_()
