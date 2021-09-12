# Created by asick
# https://github.com/asickwav/video-compressor
# Python 3.9.7 64-bit

import platform, os, subprocess, sys, psutil, asyncio, webbrowser, threading, time
import PySimpleGUI as sg
import utils as Utils

class Main:
    def __init__(self) -> None:
        self.version = "v1.1.0"
        self.author = "Asick"
        self.github = "github.com/asickwav/video-compressor"
        self.os = platform.system()
        
        # States
        self.compressing = False
        self.trimming = False
        self.trimmed = False
        self.process_started = False
        
        # UI Preferences
        self.font_large = "Arial 16 bold"
        self.font_small = "Arial 12"
        self.font_tiny = "Arial 10"

        # Options
        self.res_w = 1280
        self.res_h = 720
        self.target_file_size = 8
        self.audio_bitrate = 128
        self.fps = 30
        self.file_extension = "mp4"
        self.trim_s = "00:00:45"
        self.trim_e = "00:00:15"
        self.enable_trim = False
        self.remove_audio = False
        self.use_h265 = False
        self.portrait_mode = False

        self.selected_videos = []
        self.cur_video = ""
        self.cur_video_name = ""
        self.cur_video_path = ""
        self.cur_video_extension = ""
        self.cur_queue = 0
        self.proc = ""
        self.ffmpeg_is_valid = Utils.validate_ffmpeg()
        
        self.layout = [
            [sg.Text("%s Video Compressor %s" % (self.author, self.version), font=self.font_large)],
            [sg.Text("Resolution", font=self.font_small), sg.Input(self.res_w, font=self.font_tiny, key="res_w", size=(7, 1)), sg.Input(self.res_h, key="res_h", font=self.font_tiny, size=(7, 1))],
            [sg.Text("Target File Size", font=self.font_small), sg.Input(self.target_file_size, font=self.font_tiny, key="file_size", size=(7, 1)), sg.Text("MB")],
            [sg.Text("Audio Bitrate", font=self.font_small), sg.Input(self.audio_bitrate, font=self.font_tiny, key="audio_bitrate", size=(7, 1)), sg.Text("Kbps")],
            [sg.Text("Framerate", font=self.font_small), sg.Input(self.fps, font=self.font_tiny, key="framerate", size=(7, 1)), sg.Text("FPS")],
            [sg.Text("File Extension", font=self.font_small), sg.Input(self.file_extension, font=self.font_tiny, key="extension", size=(7, 1))],
            [sg.Text("Trim", font=self.font_small), sg.Input(self.trim_s, font=self.font_tiny, key="trim_start", size=(7, 1)), sg.Input(self.trim_e, font=self.font_tiny, key="trim_end", size=(7, 1))],
            [sg.Text("Enable Trim", font=self.font_small), sg.Checkbox("", font=self.font_tiny, default=False, key="trim", change_submits=True)],
            [sg.Text("Remove Audio", font=self.font_small), sg.Checkbox("", font=self.font_tiny, default=False, key="mute", change_submits=True)],
            [sg.Text("Use H.265 Codec", font=self.font_small), sg.Checkbox("", font=self.font_tiny, default=False, key="h265", change_submits=True)],
            [sg.Text("Portrait Mode", font=self.font_small), sg.Checkbox("", font=self.font_tiny, default=False, key="portrait", change_submits=True)],
            [sg.Text("")],
            [sg.Input("", size=(40, 1), key="select_videos", change_submits=True), sg.FilesBrowse("Select Videos", size=(10, 1))],
            [sg.Output(size=(60, 10), key="output", echo_stdout_stderr=True)],
            [sg.Button("Start", key="start", size=(8, 1)), sg.Button("Abort", key="abort", size=(8, 1)), sg.Button("Help", key="help", size=(8, 1)), sg.Button("Github", key="github", size=(8, 1))],
            [sg.Text("")],
            [sg.HorizontalSeparator(pad=None)],
            [sg.Text(f"Created by {self.author} with Python", font=self.font_tiny)],
        ]
        
        if not self.ffmpeg_is_valid:
            x = threading.Thread(target=Utils.install_ffmpeg)
            x.start()
        
        self.main()
    
    def help(self) -> None:
        sg.popup("""
            Resolution: Set your video's dimensions (width x height).
            \n\nTarget File Size: Set the targetted file size for your video.
            \n\nAudio Bitrate: Set your video's audio bitrate.
            \n\nFramerate: Set your video's fps.
            \n\nFile Extension: Set the file type of your video.
            \n\nTrim: The first box is your video's initial start time, the second box is the duration afterwards.
            \n\nEnable Trim: Must be enabled to trim your video.
            \n\nRemove Audio: Self explanitory.
            \n\nUse H.265 Codec: Set your video to use the H.265 codec for a higher quality output. If you plan on sharing your video on Discord then do NOT use this option, it will not embed.
            \n\nPortrait Mode: Flips the set width and height resolution to output verticle videos correctly. If you've already manually set the resolution to vertical dimensions then this option is ignored.
        """)
    
    def abort(self) -> None:
        for proc in psutil.process_iter():
            if "ffmpeg" in proc.name():
                p = psutil.Process(proc.pid)
                p.kill()

                try:
                    os.remove("TEMP")
                    print("Cleaned up temp files.")
                except:
                    pass

                self.compressing = False
                self.trimming = False
                self.trimmed = False
                self.process_started = False

                print("Aborting.")
    
    def main(self) -> None:
        self.window = sg.Window("%s Video Compressor" % self.author, self.layout, resizable=False, finalize=True, element_justification="center")
        
        while True:
            event, values, = self.window.read(timeout=1)

            if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
                self.abort()
                sys.exit()

            if event == "start":
                if not self.trimming and not self.compressing:
                    self.selected_videos = Utils.list_videos(values["select_videos"])
                    self.apply_options(values)
                    self.start()
                else:
                    print("Compression already begun. Click Abort if you need to restart.")
            
            if event == "abort":
                self.abort()
            
            if event == "help":
                self.help()
            
            if event == "github":
                webbrowser.open("https://github.com/asickwav/video-compressor")
        

if __name__ == "__main__":
    main = Main()