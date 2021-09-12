# Created by asick
# https://github.com/asickwav/video-compressor
# Python 3.9.7 64-bit

import platform, os, subprocess, psutil, webbrowser, threading
import PySimpleGUI as sg
import utils as Utils

sg.LOOK_AND_FEEL_TABLE["swag"] = {
    'BACKGROUND': 'white',
    'TEXT': 'black',
    'INPUT': 'white',
    'TEXT_INPUT': '#000000',
    'SCROLL': 'white',
    'BUTTON': ('white', '#2b3340'),
    'PROGRESS': ('#01826B', '#D0D0D0'),
    'BORDER': 1,
    'SLIDER_DEPTH': 0,
    'PROGRESS_DEPTH': 0
}

sg.theme("swag")

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
        self.cur_pass = 1
        self.proc = ""
        self.ffmpeg_path = Utils.get_ffmpeg_path()
        
        self.layout = [
            [sg.Text("%s Video Compressor %s" % (self.author, self.version), font=self.font_large)],
            [sg.Text("Resolution", font=self.font_small), sg.Input(self.res_w, font=self.font_tiny, key="res_w", size=(7, 1)), sg.Input(self.res_h, key="res_h", font=self.font_tiny, size=(7, 1))],
            [sg.Text("Target File Size", font=self.font_small), sg.Input(self.target_file_size, font=self.font_tiny, key="file_size", size=(7, 1)), sg.Text("MB")],
            [sg.Text("Audio Bitrate", font=self.font_small), sg.Input(self.audio_bitrate, font=self.font_tiny, key="audio_bitrate", size=(7, 1)), sg.Text("Kbps")],
            [sg.Text("Framerate", font=self.font_small), sg.Input(self.fps, font=self.font_tiny, key="framerate", size=(7, 1)), sg.Text("FPS")],
            [sg.Text("File Extension", font=self.font_small), sg.Input(self.file_extension, font=self.font_tiny, key="extension", size=(7, 1))],
            [sg.Text("Trim (hh:mm:ss)", font=self.font_small), sg.Input(self.trim_s, font=self.font_tiny, key="trim_start", size=(7, 1)), sg.Input(self.trim_e, font=self.font_tiny, key="trim_end", size=(7, 1))],
            [sg.Text("Enable Trim", font=self.font_small), sg.Checkbox("", font=self.font_tiny, default=False, key="trim", change_submits=True)],
            [sg.Text("Remove Audio", font=self.font_small), sg.Checkbox("", font=self.font_tiny, default=False, key="mute", change_submits=True)],
            [sg.Text("Use H.265 Codec", font=self.font_small), sg.Checkbox("", font=self.font_tiny, default=False, key="h265", change_submits=True)],
            [sg.Text("Portrait Mode", font=self.font_small), sg.Checkbox("", font=self.font_tiny, default=False, key="portrait", change_submits=True)],
            [sg.Text("")],
            [sg.Input("", size=(40, 1), key="select_videos", change_submits=True), sg.FilesBrowse("Select Videos", size=(10, 1))],
            [sg.Output(size=(60, 10), key="output", echo_stdout_stderr=True)],
            [sg.Button("Start", key="start", size=(8, 1)), sg.Button("Abort", key="abort", size=(8, 1)), sg.Button("Help", key="help", size=(8, 1))],
            [sg.Text("")],
            [sg.HorizontalSeparator(pad=None)],
            [sg.Text("This app is free and open-source!", font=self.font_tiny)],
            [sg.Button("Buy me a coffee", key="support", size=(15, 1)), sg.Button("Github", key="github", size=(15, 1))],
        ]
        
        self.main()
        
    def start(self, values) -> None:
        if not self.compressing and not self.trimming:
            self.apply_options(values)
            self.selected_videos = Utils.list_videos(values["select_videos"])
            
            if len(self.selected_videos) > 0:
                if not Utils.ffmpeg_installed:
                    print("Please wait for FFmpeg to finish installing.")
                else:
                    if self.enable_trim and not self.trimmed:
                        x = threading.Thread(target=self.trim)
                        x.start()
                    else:
                        x = threading.Thread(target=self.compress)
                        x.start()
            else:
                print('No videos selected!')
            
            if not Utils.ffmpeg_installed:
                print("Please wait for FFmpeg to finish installing.")
        else:
            print("Compression started, click Abort to stop.")
    
    def help(self) -> None:
        sg.popup(
            """Resolution: Set your video's dimensions (width x height).
            \n\nTarget File Size: Set the desired file size for your video(s) in MB.
            \n\nAudio Bitrate: Set the audio bitrate for your video(s) in Kbps.
            \n\nFramerate: Set the fps for your video(s).
            \n\nFile Extension: Set the file type of your video(s).
            \n\nTrim: The first box is the time where your video(s) will start, the second box is how long your video(s) will be. (This is just how FFmpeg handles trimming, I hate it too.)
            \n\nEnable Trim: Must be enabled to trim your video(s).
            \n\nRemove Audio: Self explanitory.
            \n\nUse H.265 Codec: Set your video(s) to use the H.265 codec for a higher visual quality. If you plan on sharing your video on Discord then do NOT use this option, it will not embed.
            \n\nPortrait Mode: Flips the set width and height resolution to output verticle videos correctly. If you've already manually set the resolution to vertical dimensions then this option is ignored.
        """)
    
    def abort(self) -> None:
        for proc in psutil.process_iter():
            if "ffmpeg" in proc.name():
                p = psutil.Process(proc.pid)
                p.kill()

                self.compressing = False
                self.trimming = False
                self.trimmed = False
                self.process_started = False
        
        self.cleanup()
        print("Aborted.")
    
    def apply_options(self, values) -> None:
        self.res_w = int(values["res_w"])
        self.res_h = int(values["res_h"])
        print("Set resolution to %sx%s." % (self.res_w, self.res_h))
        
        self.target_file_size = int(values["file_size"])
        print("Set target file size to %sMB." % self.target_file_size)
        
        self.audio_bitrate = int(values["audio_bitrate"])
        print("Set audio bitrate to %sk." % self.audio_bitrate)
        
        self.fps = int(values["framerate"])
        print("Set framerate to %s FPS." % self.fps)
        
        self.file_extension = "." + values["extension"]
        print("Set file extension to %s." % self.file_extension)
        
        self.trim_s = values["trim_start"]
        self.trim_e = values["trim_end"]
        self.enable_trim = values["trim"]
        self.remove_audio = values["mute"]
        
        if self.remove_audio:
            print("Muting video(s).")
            
        self.use_h265 = values["h265"]
        
        if self.use_h265:
            print("Using H.265 codec.")
            
        self.portrait_mode = values["portrait"]
        
        if self.portrait_mode:
            if self.res_h < self.res_w:
                h = self.res_h
                self.res_h = self.res_w
                self.res_w = h
                print("Using portrait mode, switching resolution.")
            else:
                print("Using portrait mode.")
    
    def cleanup(self) -> None:
        try:
            os.remove("TEMP")
            print("Cleaned up temp files.")
        except:
            print("No files to clean.")
    
    def trim(self) -> None:
        if not self.trimming:
            self.cur_video = self.selected_videos[self.cur_queue]
            self.cur_video_trimmed = '"%s%s-trimmed%s"' % (Utils.get_video_path(self.cur_video), Utils.get_video_name(self.cur_video), self.file_extension)
            input = '"%s"' % self.cur_video
            trim_start = "%s" % self.trim_s
            trim_end = "%s" % self.trim_e
            output = self.cur_video_trimmed
            cmd = "%s -y -ss %s -i %s -t %s -c copy %s" % (self.ffmpeg_path, trim_start, input, trim_end, output)
            print(cmd)

            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            self.trimming = True
            print("Trimming video %s/%s..." % (self.cur_queue + 1, len(self.selected_videos)))
            
        while self.trimming:
            stdout, stderr = self.proc.communicate()

            if self.proc.returncode == 0:
                self.trimming = False
                self.trimmed = True
                print("Trimming complete, starting compression...")
                self.compress()
            else:
                self.trimming = False
                self.trimmed = False
                print("Trimming failed, aborting...")
                self.abort()
    
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
    
    def main(self) -> None:
        self.window = sg.Window("%s Video Compressor %s" % (self.author, self.version), self.layout, element_justification="center")
        
        while True:
            event, values = self.window.read(timeout=1)

            if event in (sg.WIN_CLOSED, "Exit", "Cancel"):
                self.abort()
                quit()

            if event == "start":
                self.start(values)
            
            if event == "abort":
                self.abort()
            
            if event == "help":
                self.help()
            
            if event == "github":
                webbrowser.open("https://github.com/asickwav/video-compressor")
            
            if event == "support":
                webbrowser.open("https://ko-fi.com/V7V82NKB5")
            
            if not Utils.ffmpeg_installed:
                if not Utils.ffmpeg_is_downloading:
                    x = threading.Thread(target=Utils.install_ffmpeg)
                    x.start()
                    
                self.window.Read()
        

if __name__ == "__main__":
    main = Main()