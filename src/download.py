import os
import requests
import shutil
import src.globals as g
import zipfile
from PyQt6.QtCore import QThread, pyqtSignal

FFMPEG_DL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"


class DownloadThread(QThread):
    update_log = pyqtSignal(str)
    update_progress = pyqtSignal(int)
    installed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def download_ffmpeg(self):
        print("Downloading FFmpeg...")
        bin_path = g.bin_dir
        file_path = os.path.join(bin_path, "ffmpeg.zip")
        response = requests.get(FFMPEG_DL, stream=True)

        if not response.ok:
            print(f"Download failed: {response.status_code}\n{response.text}")
            return

        print(f"Source: {FFMPEG_DL}")
        total_size = response.headers.get("content-length")

        with open(file_path, "wb") as f:
            if total_size is None:
                f.write(response.content)
            else:
                downloaded = 0
                total_size = int(total_size)

                for chunk in response.iter_content(chunk_size=4096):
                    downloaded += len(chunk)
                    f.write(chunk)
                    percentage = (downloaded / total_size) * 100
                    downloaded_mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    message = f"Downloading FFmpeg...\n{downloaded_mb:.1f} MB / {total_mb:.1f} MB"
                    self.update_log.emit(message)
                    self.update_progress.emit(int(percentage))

    def install_ffmpeg(self):
        print("Installing FFmpeg...")
        zip_path = os.path.join(g.bin_dir, "ffmpeg.zip")

        # Extract files
        with zipfile.ZipFile(zip_path, "r") as zip_file:
            zip_file.extractall(g.bin_dir)
        os.remove(zip_path)

        # Get extracted paths
        extracted_root = os.path.join(g.bin_dir, os.listdir(g.bin_dir)[0])
        extracted_bin = os.path.join(extracted_root, "bin")

        # Move binaries to target directory
        for file_name in os.listdir(extracted_bin):
            src = os.path.join(extracted_bin, file_name)
            dst = os.path.join(g.bin_dir, file_name)
            try:
                shutil.move(src, dst)
            except:
                print(f"Skipped {file_name} - file already exists")

        # Cleanup
        shutil.rmtree(extracted_root)
        os.remove(os.path.join(g.bin_dir, "ffplay.exe"))

    def run(self):
        self.download_ffmpeg()
        self.install_ffmpeg()
        self.installed.emit()
