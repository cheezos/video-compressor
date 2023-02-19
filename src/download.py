import os
import requests
import shutil
import src.globals as g
import zipfile
from src.utils import *
from PyQt6.QtCore import QThread, pyqtSignal


class DownloadThread(QThread):
    update_label = pyqtSignal(str)
    installed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def _download_ffmpeg(self):
        print("Downloading FFmpeg...")
        BIN_PATH = g.dir_bin
        URL = g.FFMPEG_DL
        FILE_PATH = f"{BIN_PATH}/ffmpeg.zip"

        if os.path.exists(FILE_PATH):
            print("Download complete")
        else:
            R = requests.get(URL, stream=True)

            if R.ok:
                print(f"Downloading from {URL}")
                TOTAL_LENGTH = R.headers.get("content-length")

                with open(FILE_PATH, "wb") as F:
                    if TOTAL_LENGTH == None:
                        F.write(R.content)
                    else:
                        dl = 0
                        TOTAL_LENGTH = int(TOTAL_LENGTH)

                        for DATA in R.iter_content(chunk_size=4096):
                            dl += len(DATA)
                            F.write(DATA)
                            CHAR_COUNT = int(20 * dl / TOTAL_LENGTH)
                            DL_CHARS = "=" * CHAR_COUNT
                            EMPTY_CHARS = "  " * (20 - CHAR_COUNT)
                            PROGRESS = f"{dl}/{TOTAL_LENGTH}"
                            TEXT = f"This app relies on FFmpeg to compress the videos, please wait while it downloads...\n\n{PROGRESS}\n[{DL_CHARS}{EMPTY_CHARS}]"
                            self.update_label.emit(TEXT)

                    print("Download complete")
            else:
                print(f"Download failed: {R.status_code}\n{R.text}")

    def _install_ffmpeg(self):
        print("Installing FFmpeg...")
        BIN_PATH = g.dir_bin
        FILE_PATH = f"{BIN_PATH}/ffmpeg.zip"
        print("Extracting FFmpeg...")

        with zipfile.ZipFile(FILE_PATH, "r") as F:
            F.extractall(BIN_PATH)

        print("FFmpeg extracted")
        print("Moving extracted files to bin folder...")
        print("Deleting FFmpeg 7z file...")
        os.remove(FILE_PATH)
        print("Deleted")
        EXTRACTED_PATH = f"{BIN_PATH}/{os.listdir(BIN_PATH)[0]}"
        EXTRACTED_BIN_PATH = f"{BIN_PATH}/{os.listdir(BIN_PATH)[0]}/bin"
        FILES = os.listdir(EXTRACTED_BIN_PATH)

        for FILE_NAME in FILES:
            print(f"Moving {FILE_NAME}...")
            FILE_PATH = f"{EXTRACTED_BIN_PATH}/{FILE_NAME}"

            try:
                shutil.move(FILE_PATH, BIN_PATH)
            except:
                print(f"Failed to move {FILE_NAME}, probably already exists")

        print("Files moved")
        print("Deleting temp files")

        try:
            shutil.rmtree(EXTRACTED_PATH)
            os.remove(f"{BIN_PATH}/ffplay.exe")
            print("Deleted")
        except:
            print("No temp files to delete")

        self.update_label.emit(g.READY_TEXT)

    def run(self):
        self._download_ffmpeg()
        self._install_ffmpeg()
        self.installed.emit()
