import subprocess
import os
import src.globals as g
from src.utils import *
from PyQt6.QtCore import QThread, pyqtSignal


class CompressionThread(QThread):
    update_label = pyqtSignal(str)
    completed = pyqtSignal()

    def __init__(self, target_file_size, parent=None):
        super().__init__(parent)
        self._target_file_size = target_file_size
        self.process = None

    def _run_pass(self, file_path, bitrate, pass_1: bool):
        COMPLETED_COUNT = len(g.completed) + 1
        QUEUE_COUNT = len(g.queue)
        PASS = "1" if pass_1 else "2"
        MSG = f"Compressing, please wait...\n\nVideo queue: {COMPLETED_COUNT}/{QUEUE_COUNT}\nPass: {PASS}/2"
        FILE_NAME = file_path.split("/")[-1]
        FFMPEG = g.ffmpeg_path
        INPUT = file_path
        BITRATE = f"{bitrate}k"
        print(f"New bitrate: {BITRATE}")
        OUTPUT = rf"{g.dir_output}/{FILE_NAME}-compressed.mp4"
        print(MSG)
        cmd = ""

        if pass_1:
            cmd = r""""%s" -i "%s" -y -b:v %s -an -pass 1 -f mp4 TEMP""" % (
                FFMPEG,
                INPUT,
                BITRATE,
            )
        else:
            cmd = r""""%s" -i "%s" -y -b:v %sk -b:a %sk -pass 2 "%s" """ % (
                g.ffmpeg_path,
                file_path,
                bitrate,
                128,
                OUTPUT,
            )

        print(cmd)
        self.update_label.emit(MSG)
        self.process = subprocess.check_call(
            cmd,
            shell=True,
        )

    def run(self):
        g.completed = []

        for FILE_PATH in g.queue:
            if not g.compressing:
                break

            BITRATE = get_video_bitrate(FILE_PATH, self._target_file_size)
            self._run_pass(FILE_PATH, BITRATE, True)
            self._run_pass(FILE_PATH, BITRATE, False)
            clean()
            g.completed.append(FILE_PATH)

        COMPLETED_COUNT = len(g.completed)
        PLURAL = "s" if COMPLETED_COUNT > 1 else ""
        msg = f"Compressed {COMPLETED_COUNT} video{PLURAL}!"

        if not g.compressing:
            msg = "Aborted!"

        print(msg)
        self.update_label.emit(msg)
        self.completed.emit()
