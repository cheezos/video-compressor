import json
import sys
import os
import os
import psutil
import globals as g
from notifypy import Notify
from download import DownloadThread
from thread import CompressionThread
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QLineEdit,
    QCheckBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from rect import Rect

VERSION = "3.1.0"
TITLE = f"CVC v{VERSION}"
READY_TEXT = f"Select your videos to get started."

# Window dimensions
WINDOW = Rect(0, 0, 250, 400)
WINDOW_HALF = Rect(0, 0, WINDOW.w // 2, WINDOW.h // 2)

BUTTON_DISABLED = "background-color: #666666; color: #cccccc;"
BUTTON_SELECT = "background-color: #039dfc; color: white; font-weight: bold;"
BUTTON_COMPRESS = "background-color: #4CAF50; color: white; font-weight: bold;"
BUTTON_ABORT = "background-color: #f44336; color: white; font-weight: bold;"

# Gaps
H_GAP = 5
V_GAP = 5

# Buttons and elements
SELECT_BUTTON = Rect(
    WINDOW_HALF.w - (WINDOW.w - H_GAP) // 2,
    V_GAP,  # Start with V_GAP from top
    WINDOW.w - H_GAP,
    50,
)

COMPRESS_BUTTON = Rect(
    SELECT_BUTTON.x,
    SELECT_BUTTON.y + SELECT_BUTTON.h + V_GAP,  # Add V_GAP after select button
    SELECT_BUTTON.w // 2 - H_GAP // 4,
    SELECT_BUTTON.h,
)

ABORT_BUTTON = Rect(
    COMPRESS_BUTTON.x + COMPRESS_BUTTON.w + H_GAP // 2,
    COMPRESS_BUTTON.y,
    COMPRESS_BUTTON.w,
    COMPRESS_BUTTON.h,
)

FILE_SIZE_LABEL = Rect(
    COMPRESS_BUTTON.x,
    COMPRESS_BUTTON.y + COMPRESS_BUTTON.h + V_GAP,  # Add V_GAP after buttons
    COMPRESS_BUTTON.w - 5,
    25,
)

FILE_SIZE_ENTRY = Rect(
    ABORT_BUTTON.x, FILE_SIZE_LABEL.y, ABORT_BUTTON.w, FILE_SIZE_LABEL.h
)

GPU_LABEL = Rect(
    COMPRESS_BUTTON.x,
    FILE_SIZE_ENTRY.y + FILE_SIZE_ENTRY.h + V_GAP,  # Add V_GAP after size entry
    COMPRESS_BUTTON.w - 5,
    25,
)

GPU_CHECKBOX = Rect(ABORT_BUTTON.x, GPU_LABEL.y, 25, 25)

LOG_AREA = Rect(
    SELECT_BUTTON.x,
    GPU_CHECKBOX.y + GPU_CHECKBOX.h + V_GAP,  # Add V_GAP after checkbox
    SELECT_BUTTON.w,
    WINDOW.h - SELECT_BUTTON.y - GPU_CHECKBOX.y - GPU_CHECKBOX.h - V_GAP,
)

DEFAULT_SETTINGS = {"target_size": 20.0, "use_gpu": False}


def load_settings():
    try:
        with open(os.path.join(g.res_dir, "settings.json"), "r") as f:
            return json.load(f)
    except:
        return DEFAULT_SETTINGS


def save_settings(settings):
    with open(os.path.join(g.res_dir, "settings.json"), "w") as f:
        json.dump(settings, f)


def clean():
    try:
        os.remove(os.path.join(g.root_dir, "TEMP"))
        os.remove(os.path.join(g.root_dir, "ffmpeg2pass-0.log"))
        os.remove(os.path.join(g.root_dir, "ffmpeg2pass-0.log.mbtree"))
    except:
        pass


def kill_ffmpeg():
    for proc in psutil.process_iter():
        if "ffmpeg" in proc.name():
            proc.kill()


def delete_bin():
    print("@@@@@@@@@@@@@@@@@@@@@@ DELETING BIN @@@@@@@@@@@@@@@@@@@@@@@")
    for root, dirs, files in os.walk(g.bin_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


class Window(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.verify_directories()
        self.settings = load_settings()
        self.setFixedSize(WINDOW.w, WINDOW.h)
        self.setWindowTitle(TITLE)
        icon_path = os.path.join(g.res_dir, "icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        # Select Button
        self.button_select = QPushButton("Select Videos", self)
        self.button_select.resize(SELECT_BUTTON.w, SELECT_BUTTON.h)
        self.button_select.move(SELECT_BUTTON.x, SELECT_BUTTON.y)
        self.button_select.clicked.connect(self.select_videos)
        self.button_select.setEnabled(False)

        # Compress Button
        self.button_compress = QPushButton("Compress", self)
        self.button_compress.resize(COMPRESS_BUTTON.w, COMPRESS_BUTTON.h)
        self.button_compress.move(COMPRESS_BUTTON.x, COMPRESS_BUTTON.y)
        self.button_compress.clicked.connect(self.compress_videos)
        self.button_compress.setEnabled(False)

        # Abort Button
        self.button_abort = QPushButton("Abort", self)
        self.button_abort.resize(ABORT_BUTTON.w, ABORT_BUTTON.h)
        self.button_abort.move(ABORT_BUTTON.x, ABORT_BUTTON.y)
        self.button_abort.clicked.connect(self.abort_compression)
        self.button_abort.setEnabled(False)

        # File Size Label
        self.label_size = QLabel("Target Size (MB)", self)
        self.label_size.resize(FILE_SIZE_LABEL.w, FILE_SIZE_LABEL.h)
        self.label_size.move(FILE_SIZE_LABEL.x, FILE_SIZE_LABEL.y)
        self.label_size.setAlignment(Qt.AlignmentFlag.AlignRight)

        # File Size Entry
        self.edit_size = QLineEdit(str(self.settings["target_size"]), self)
        self.edit_size.resize(FILE_SIZE_ENTRY.w, FILE_SIZE_ENTRY.h)
        self.edit_size.move(FILE_SIZE_ENTRY.x, FILE_SIZE_ENTRY.y)
        self.edit_size.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.edit_size.setEnabled(True)

        # GPU Label
        self.label_gpu = QLabel("Use GPU", self)
        self.label_gpu.resize(GPU_LABEL.w, GPU_LABEL.h)
        self.label_gpu.move(GPU_LABEL.x, GPU_LABEL.y)
        self.label_gpu.setAlignment(Qt.AlignmentFlag.AlignRight)

        # GPU Checkbox
        self.checkbox_gpu = QCheckBox(self)
        self.checkbox_gpu.resize(GPU_CHECKBOX.w, GPU_CHECKBOX.h)
        self.checkbox_gpu.move(GPU_CHECKBOX.x, GPU_CHECKBOX.y)
        self.checkbox_gpu.setChecked(self.settings["use_gpu"])

        # Log Label
        self.label_log = QLabel(READY_TEXT, self)
        self.label_log.setEnabled(True)
        self.label_log.resize(LOG_AREA.w, LOG_AREA.h)
        self.label_log.move(LOG_AREA.x, LOG_AREA.y)
        self.label_log.setWordWrap(True)
        self.label_log.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_log.setStyleSheet("border: 1px solid black; margin: 1px")

        self.download_thread = None
        self.compress_thread = None

        self.button_select.setStyleSheet(BUTTON_DISABLED)
        self.button_compress.setStyleSheet(BUTTON_DISABLED)
        self.button_abort.setStyleSheet(BUTTON_DISABLED)

        self.verify_ffmpeg()

    def reset(self):
        g.compressing = False
        g.queue = []
        self.button_select.setEnabled(True)
        self.button_select.setStyleSheet(BUTTON_SELECT)
        self.button_select.setFocus()
        self.button_compress.setEnabled(False)
        self.button_compress.setStyleSheet(BUTTON_DISABLED)
        self.button_abort.setEnabled(False)
        self.button_abort.setStyleSheet(BUTTON_DISABLED)
        self.edit_size.setEnabled(True)
        self.update_log(READY_TEXT)

    def closeEvent(self, event):
        # Save settings when closing
        self.settings["last_videos"] = g.queue
        self.settings["target_size"] = float(self.edit_size.text())
        self.settings["use_gpu"] = self.checkbox_gpu.isChecked()
        save_settings(self.settings)
        kill_ffmpeg()
        event.accept()

    def select_videos(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Video Files",
            "",
            "Video Files (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm *.m4v);;All Files (*.*)",
        )

        if len(file_paths) > 0:
            for PATH in file_paths:
                if PATH in g.queue:
                    continue

                g.queue.append(PATH)

            self.button_compress.setEnabled(True)
            self.button_compress.setStyleSheet(BUTTON_COMPRESS)
            print(f"Selected: {g.queue}")
            msg = f"Selected {len(g.queue)} video(s)."
            self.update_log(msg)

    def compress_videos(self):
        g.compressing = True
        self.button_select.setStyleSheet(BUTTON_DISABLED)
        self.button_compress.setStyleSheet(BUTTON_DISABLED)
        self.button_abort.setEnabled(True)
        self.button_abort.setStyleSheet(BUTTON_ABORT)
        self.button_select.setEnabled(False)
        self.button_compress.setEnabled(False)
        self.edit_size.setEnabled(False)
        self.compress_thread = CompressionThread(
            float(self.edit_size.text()), self.checkbox_gpu.isChecked()
        )
        self.compress_thread.completed.connect(self.completed)
        self.compress_thread.update_label.connect(self.update_log)
        self.compress_thread.start()

    def abort_compression(self):
        kill_ffmpeg()
        self.completed(True)

    def update_log(self, text):
        self.label_log.setText(text)

    def installed(self):
        BIN_PATH = g.bin_dir
        g.ffmpeg_installed = True
        g.ffmpeg_path = os.path.join(BIN_PATH, "ffmpeg.exe")
        g.ffprobe_path = os.path.join(BIN_PATH, "ffprobe.exe")
        self.reset()
        n = Notify()
        n.title = "FFmpeg installed!"
        n.message = "You can now compress your videos."
        n.icon = os.path.join(g.res_dir, "icon.ico")
        n.send()

    def completed(self, aborted=False):
        g.compressing = False
        self.compress_thread.terminate()
        self.reset()
        n = Notify()
        n.title = "Done!" if not aborted else "Aborted!"
        n.message = "Your videos are ready." if not aborted else "Compression aborted!"
        n.icon = os.path.join(g.res_dir, "icon.ico")
        n.send()

        if not aborted:
            os.startfile(g.output_dir)

    def verify_directories(self):
        print("Verifying directories...")
        g.root_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"Root: {g.root_dir}")
        g.bin_dir = os.path.join(g.root_dir, "bin")

        if not os.path.exists(g.bin_dir):
            os.mkdir(g.bin_dir)

        print(f"Bin: {g.bin_dir}")
        g.output_dir = os.path.join(g.root_dir, "output")

        if not os.path.exists(g.output_dir):
            os.mkdir(g.output_dir)

        print(f"Output: {g.output_dir}")
        g.res_dir = os.path.join(g.root_dir, "res")
        print(f"Res: {g.res_dir}")

    def verify_ffmpeg(self):
        print("Verifying FFmpeg...")
        FFMPEG_PATH = os.path.join(g.bin_dir, "ffmpeg.exe")
        print(f"FFmpeg: {FFMPEG_PATH}")
        FFPROBE_PATH = os.path.join(g.bin_dir, "ffprobe.exe")
        print(f"FFprobe: {FFPROBE_PATH}")

        if os.path.exists(FFMPEG_PATH) and os.path.exists(FFPROBE_PATH):
            g.ffmpeg_installed = True
            g.ffmpeg_path = FFMPEG_PATH
            g.ffprobe_path = FFPROBE_PATH
            self.reset()
        else:
            self.download_thread = DownloadThread()
            self.download_thread.installed.connect(self.installed)
            self.download_thread.update_label.connect(self.update_log)
            self.download_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
