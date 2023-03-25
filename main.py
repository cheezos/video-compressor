import sys
import os
import platform
import subprocess
import webbrowser
import src.globals as g
from notifypy import Notify
from src.utils import clean, kill_ffmpeg
from src.download import DownloadThread
from src.thread import CompressionThread
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QLineEdit,
)
from PyQt6.QtCore import Qt


class Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        W, H = g.W_SIZE
        BW, BH = g.B_SIZE
        SBW, SBH = g.SB_SIZE
        self.setFixedSize(W, H)
        self.setWindowTitle(g.TITLE)
        self._button_select = QPushButton("Select Videos", self)
        self._button_select.resize(BW, BH)
        X, Y = g.B_SEL_POS
        self._button_select.move(X, Y)
        self._button_select.clicked.connect(self._select_videos)
        self._button_select.setEnabled(g.ffmpeg_installed)
        self._button_compress = QPushButton("Compress", self)
        self._button_compress.resize(BW, BH)
        X, Y = g.B_COMP_POS
        self._button_compress.move(X, Y)
        self._button_compress.clicked.connect(self._compress_videos)
        self._button_compress.setEnabled(False)
        self._button_abort = QPushButton("Abort", self)
        self._button_abort.resize(BW, BH)
        X, Y = g.B_ABORT_POS
        self._button_abort.move(X, Y)
        self._button_abort.clicked.connect(self._abort_compression)
        self._button_abort.setEnabled(False)
        self._label_size = QLabel("File Size (MB)", self)
        self._label_size.resize(g.L_FS_SIZE[0], g.L_FS_SIZE[1])
        X, Y = g.B_FS_POS
        self._label_size.move(X, Y)
        self._label_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._edit_size = QLineEdit("8.0", self)
        self._edit_size.resize(g.E_FS_SIZE[0], g.E_FS_SIZE[1])
        X, Y = g.E_FS_POS
        self._edit_size.move(X, Y)
        self._edit_size.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._edit_size.setEnabled(True)
        self._label_log = QLabel(g.READY_TEXT, self)
        self._label_log.setEnabled(True)
        self._label_log.resize(g.L_LOG_SIZE[0], g.L_LOG_SIZE[1])
        X, Y = g.L_LOG_POS
        self._label_log.move(X, Y)
        self._label_log.setWordWrap(True)
        self._label_log.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label_log.setStyleSheet("border: 1px solid black; margin: 1px")
        self._button_foot = QPushButton(f"v{g.VERSION}", self)
        self._button_foot.resize(SBW, SBH)
        X, Y = g.B_FOOT_POS
        self._button_foot.move(X, Y)
        self._button_foot.clicked.connect(self._open_github)
        self._button_foot.setEnabled(True)
        self._download_thread = None
        self._compress_thread = None
        self._verify_directories()
        self._verify_ffmpeg()

    def _reset(self):
        g.compressing = False
        self._button_select.setEnabled(True)
        self._button_select.setFocus()
        self._button_compress.setEnabled(False)
        self._button_abort.setEnabled(False)
        self._edit_size.setEnabled(True)
        self._update_log(g.READY_TEXT)

    def _select_videos(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Videos",
            "",
            "MP4 Files (*.mp4);; WebM Files (*.webm);; All Files (*.*)",
        )

        if len(file_paths) > 0:
            for PATH in file_paths:
                if PATH in g.queue:
                    continue

                g.queue.append(PATH)

            self._button_compress.setEnabled(True)
            print(f"Selected: {g.queue}")
            COUNT = len(g.queue)
            PLURAL = "s" if COUNT > 1 else ""
            TEXT = f"Selected {len(g.queue)} video{PLURAL}.\n\nSet your desired file size for these videos and click Compress."
            self._update_log(TEXT)

    def _compress_videos(self):
        g.compressing = True
        self._button_select.setEnabled(False)
        self._button_compress.setEnabled(False)
        self._button_abort.setEnabled(True)
        self._edit_size.setEnabled(False)
        self._compress_thread = CompressionThread(float(self._edit_size.text()))
        self._compress_thread.completed.connect(self._completed)
        self._compress_thread.update_label.connect(self._update_log)
        self._compress_thread.start()

    def _abort_compression(self):
        kill_ffmpeg()
        self._completed(True)

    def _open_github(self):
        webbrowser.open("https://github.com/cheezos/video-compressor")

    def _update_log(self, text):
        self._label_log.setText(text)

    def _installed(self):
        BIN_PATH = g.dir_bin
        g.ffmpeg_installed = True
        g.ffmpeg_path = f"{BIN_PATH}/ffmpeg.exe"
        g.ffprobe_path = f"{BIN_PATH}/ffprobe.exe"
        self._reset()
        N = Notify()
        N.title = "FFmpeg installed!"
        N.message = "You can now compress your videos."
        N.send()

    def _completed(self, aborted=False):
        g.compressing = False
        self._compress_thread.terminate()
        self._reset()
        N = Notify()
        N.title = "Done!" if not aborted else "Aborted!"
        N.message = ""
        N.send()

        if not aborted:
            if platform.system() == "Windows":
                os.startfile(g.dir_output)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", g.dir_output])
            else:
                subprocess.Popen(["xdg-open", g.dir_output])

    def _verify_directories(self):
        print("Verifying directories...")
        g.dir_root = os.path.dirname(os.path.abspath(__file__))
        print(f"Root: {g.dir_root}")
        g.dir_bin = os.path.join(g.dir_root, "bin")

        if not os.path.exists(g.dir_bin):
            os.mkdir(g.dir_bin)
            print(f"Created bin directory")

        print(f"Bin: {g.dir_bin}")
        g.dir_output = os.path.join(g.dir_root, "output")

        if not os.path.exists(g.dir_output):
            os.mkdir(g.dir_output)
            print(f"Created output directory")

        print(f"Output: {g.dir_output}")
        print("Directories verified")

    def _handle_windows(self):
        print("Windows detected")
        FFMPEG_PATH = os.path.join(g.dir_bin, "ffmpeg.exe")
        print(f"FFmpeg: {FFMPEG_PATH}")
        FFPROBE_PATH = os.path.join(g.dir_bin, "ffprobe.exe")
        print(f"FFprobe: {FFPROBE_PATH}")

        if os.path.exists(FFMPEG_PATH) and os.path.exists(FFPROBE_PATH):
            BIN_PATH = g.dir_bin
            g.ffmpeg_installed = True
            g.ffmpeg_path = FFMPEG_PATH
            g.ffprobe_path = FFPROBE_PATH
            self._button_select.setEnabled(True)
        else:
            self._download_thread = DownloadThread()
            self._download_thread.installed.connect(self._installed)
            self._download_thread.update_label.connect(self._update_log)
            self._download_thread.start()

    def _handle_darwin(self):
        print("Darwin detected")
        CMD = "ffmpeg"
        PROCESS = subprocess.Popen(
            CMD, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )

        while True:
            OUTPUT = PROCESS.stdout.readline().strip().decode("utf-8")
            OUTPUT_ERR = PROCESS.stderr.readline().strip().decode("utf-8")

            if not "not found" in OUTPUT_ERR:
                g.ffmpeg_installed = True
                self._reset()

            if OUTPUT == "" and PROCESS.poll() is not None:
                break

    def _verify_ffmpeg(self):
        print("Verifying FFmpeg...")

        if g.platform == "Windows":
            self._handle_windows()
        else:
            self._handle_darwin()

        print("FFmpeg verified" if g.ffmpeg_installed else "FFmpeg not installed!")


if __name__ == "__main__":
    clean()
    g.platform = platform.system()
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
