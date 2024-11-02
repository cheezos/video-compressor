## Cheezos Video Compressor

A no bullshit video compressor.

## Features

- Compresses multiple videos in a queue system
- Target any specific output file size in MB
- Supports GPU acceleration (NVIDIA, Intel QuickSync, AMD)
- Automatically downloads and installs FFmpeg (Windows)
- Progress tracking with detailed status updates
- Supports multiple video formats (mp4, avi, mkv, mov, wmv, flv, webm, m4v)
- Two-pass encoding for optimal quality
- Automatic bitrate calculation
- Desktop notifications on completion
- Preserves audio quality
- Clean and simple user interface, no bullshit!
- Settings persistence between sessions
- Auto-opens output folder when complete

### New version on Patreon!

[![Patreon](https://github.com/cheezos/video-compressor/blob/main/patreon.png)](https://www.patreon.com/cheezos/shop/cheezos-video-compressor-616355?utm_medium=clipboard_copy&utm_source=copyLink&utm_campaign=productshare_creator&utm_content=join_link)

## Build

### Easy Way
1. Clone the repository.
2. Run setup.bat

### Hard Way
1. Open a terminal.
2. Clone the repository with `git clone https://github.com/cheezos/video-compressor.git`
3. Enter the project directory with `cd video-compressor`
4. Create a virtual environment with `python -m venv .venv`
5. Activate the virtual environment with `.\.venv\Scripts\activate`
6. Install the required packages with `pip install -r requirements.txt`
7. Build the application with `python setup.py build`

### The Result

![Preview](https://github.com/cheezos/video-compressor/blob/main/preview.png)

---

Created with Python 3.12.6, PyQt6 and the latest FFmpeg.
