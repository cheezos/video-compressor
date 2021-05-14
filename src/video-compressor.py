# Created by Colt
# https://github.com/colthub/video-compressor
# Python 3.8.5 64-bit

import platform
import os
import subprocess
import sys
from typing import Sized
import psutil
import PySimpleGUI as sg

from utils import validate_ffmpeg, list_videos, get_name, get_extension, get_path, get_ffmpeg, calculate_video_bitrate, install_ffmpeg

class App:
    def __init__(self) -> None:
        self.version = 'v1.0.0'
        self.author = 'Colt'
        self.github = 'github.com/colthub/video-compressor'
        self.os = platform.system()

        # States
        self.ffmpeg_installed = False
        self.compressing = False
        self.trimming = False
        self.trimmed = False

        # UI Preferences
        self.font_large = 'Arial 14 bold'
        self.font_small = 'Arial 12'

        # Options
        self.res_w = 1280
        self.res_h = 720
        self.target_file_size = 8
        self.audio_bitrate = 128
        self.fps = 30
        self.file_extension = 'mp4'
        self.trim_s = '00:00:45'
        self.trim_e = '00:00:15'
        self.enable_trim = False
        self.remove_audio = False
        self.use_h265 = False
        self.portrait_mode = False

        self.selected_videos = []
        self.cur_video = ''
        self.cur_video_name = ''
        self.cur_video_path = ''
        self.cur_video_extension = ''
        self.cur_queue = 0
        self.proc = ''
        self.ffmpeg = get_ffmpeg()

        # Layout
        options_column_left = [
            [sg.Text('Resolution', font=self.font_small)],
            [sg.Text('Target File Size', font=self.font_small)],
            [sg.Text('Audio Bitrate', font=self.font_small)],
            [sg.Text('Framerate', font=self.font_small)],
            [sg.Text('File Extension', font=self.font_small)],
            [sg.Text('Trim', font=self.font_small)],
            [sg.Text('Enable Trim', font=self.font_small)],
            [sg.Text('Remove Audio', font=self.font_small)],
            [sg.Text('Use H.265 Codec', font=self.font_small)],
            [sg.Text('Portrait Mode', font=self.font_small)]
        ]

        options_column_right = [
            [sg.Input(self.res_w, font=self.font_small, key='res_w', size=(7, 1)), sg.Input(self.res_h, key='res_h', font=self.font_small, size=(7, 1))],
            [sg.Input(self.target_file_size, font=self.font_small, key='file_size', size=(7, 1)), sg.Text('MB')],
            [sg.Input(self.audio_bitrate, font=self.font_small, key='audio_bitrate', size=(7, 1)), sg.Text('Kbps')],
            [sg.Input(self.fps, font=self.font_small, key='framerate', size=(7, 1)), sg.Text('FPS')],
            [sg.Input(self.file_extension, font=self.font_small, key='extension', size=(7, 1))], 
            [sg.Input(self.trim_s, font=self.font_small, key='trim_start', size=(7, 1)), sg.Input(self.trim_e, font=self.font_small, key='trim_end', size=(7, 1))], 
            [sg.Checkbox('', font=self.font_small, default=False, key='trim', change_submits=True)],
            [sg.Checkbox('', font=self.font_small, default=False, key='mute', change_submits=True)],
            [sg.Checkbox('', font=self.font_small, default=False, key='h265', change_submits=True)],
            [sg.Checkbox('', font=self.font_small, default=False, key='portrait', change_submits=True)]
        ]

        self.layout = [
            [sg.Text(f"{self.author}'s Video Compressor", font=self.font_large)],
            [sg.Text(f"{self.version} | {self.github}", font=self.font_small)],
            [sg.HorizontalSeparator(pad=None)],
            [sg.Text('', pad=(0, 0), key='col_left'), sg.Column(options_column_left, vertical_alignment='right', element_justification='right'),
             sg.VerticalSeparator(pad=None),
             sg.Column(options_column_right, vertical_alignment='left', element_justification='left'), sg.Text('', pad=(0, 0), key='col_right')],
            [sg.HorizontalSeparator(pad=None)],
            [sg.Input('', size=(40, 1), key='select_videos', change_submits=True), sg.FilesBrowse('Select Videos', size=(10, 1))],
            [sg.Output(size=(60, 10), key='output', echo_stdout_stderr=True)],
            [sg.Button('Start', key='start', size=(10, 1)), sg.Button('Abort', disabled=True, tooltip='Disabled until asynchronous solution is implemented.', size=(10, 1)), sg.Button('Help', key='help', size=(10, 1))]
        ]

        self.ui()

    def apply_options(self, values) -> None:
        self.res_w = int(values['res_w'])
        self.res_h = int(values['res_h'])
        print(f'Set resolution to {self.res_w} x {self.res_h}.')
        self.target_file_size = int(values['file_size'])
        print(f'Set target file size to {self.target_file_size}.')
        self.audio_bitrate = int(values['audio_bitrate'])
        print(f'Set audio bitrate to {self.audio_bitrate}.')
        self.fps = float(values['framerate'])
        print(f'Set framerate to {self.fps}fps.')
        self.file_extension = '.' + values['extension']
        print(f'Set extension to {self.file_extension}.')
        self.trim_s = values['trim_start']
        self.trim_e = values['trim_end']
        self.enable_trim = values['trim']
        self.remove_audio = values['mute']
        if self.remove_audio: print('Muting video(s).')
        self.use_h265 = values['h265']
        if self.use_h265: print('Using H.265 codec.')
        self.portrait_mode = values['portrait']
        if self.portrait_mode:
            if self.res_h < self.res_w:
                h = self.res_h
                self.res_h = self.res_w
                self.res_w = h
                print('Using portrait mode, switching resolution.')
            else:
                print('Using portrait mode.')

    def start(self) -> None:
        if not validate_ffmpeg():
            print("Couldn't locate FFmpeg, please install it first.")
            return

        if not self.selected_videos or len(self.selected_videos) == 0:
            print('No videos selected!')
        else:
            if not self.compressing and not self.trimming:
                self.get_video_data(self.selected_videos[self.cur_queue])

                if self.enable_trim and not self.trimmed:
                    self.trim()
                else:
                    self.compress() 

            if (self.trimming):
                self.trim_loop()
            elif (self.compressing):
                self.compression_loop()
    
    def trim_loop(self) -> None:
        while (self.trimming):
            line = str(self.proc.stdout.readline())

            if self.proc.poll() or any(x in line for x in ['', 'failed']):
                self.trimming = False
                self.trimmed = True
                print('Trimming complete, starting compression.')
                self.start()
    
    def compression_loop(self) -> None:
        while (self.compressing):
            line = str(self.proc.stdout.readline())

            if self.proc.poll() or any(x in line for x in ['', 'failed']):                
                self.compressing = False
                self.trimmed = False
                print(f'Video {self.cur_queue + 1}/{len(self.selected_videos)} compressed.')

                try:
                    os.remove(self.cur_video_trimmed)
                    print('Deleting trimmed copy.')
                except:
                    pass

                if (self.cur_queue + 1 < len(self.selected_videos)):
                    self.cur_queue += 1
                    self.start()
                else:
                    print('Job done!')

    def trim(self) -> None:
        input = f'-i "{self.cur_video}"'
        trim_start = f'-ss {self.trim_s}'
        trim_end = f'-t {self.trim_e}'
        output = f'"{self.cur_video_trimmed}"'

        cmd = f'{self.ffmpeg} -y {trim_start} {input} {trim_end} -c copy {output}'

        if not self.trimming: 
            try:
                self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            except:
                print('Something went wrong, try changing your settings.')
                return

        self.trimming = True
        print(f'Trimming {self.cur_video} from {self.trim_s} to {self.trim_e}, please wait...')

    def compress(self) -> None:
        if self.trimmed:
            self.cur_video = self.cur_video_trimmed
            print(f'Using trimmed version: {self.cur_video_trimmed}')

        if not calculate_video_bitrate(self.cur_video, self.target_file_size, self.audio_bitrate):
            self.abort()
            return

        input = f'-i "{self.cur_video}"'
        codec = '-c:v libx265' if self.use_h265 else '-c:v libx264'
        video_bitrate = f'-b:v {calculate_video_bitrate(self.cur_video, self.target_file_size, self.audio_bitrate)}k'
        audio_bitrate = f'-c:a aac -b:a {self.audio_bitrate}k' if not self.remove_audio else '-an'
        fps = f'-r {self.fps}'
        resolution = f'-vf scale={self.res_w}:{self.res_h}'
        output = f'"{self.cur_video_path}{self.cur_video_name}-compressed{self.file_extension}"'

        cmd = f'{self.ffmpeg} -y {input} {codec} {video_bitrate} {fps} {resolution} -pass 1 -an -f mp4 TEMP && {self.ffmpeg} -y {input} {codec} {video_bitrate} {fps} {resolution} -pass 2 {audio_bitrate} {output}'
        
        if not self.compressing: 
            try:
                self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
            except:
                print('Something went wrong, try changing your settings.')
                return

        self.compressing = True
        print(f'Compressing video {self.cur_queue + 1}/{len(self.selected_videos)}, please wait...')

    def get_video_data(self, video) -> None:
        self.cur_video = video
        self.cur_video_name = get_name(self.cur_video)
        self.cur_video_path = get_path(self.cur_video)
        self.cur_video_extension = get_extension(self.cur_video)
        self.cur_video_trimmed = f'{self.cur_video_path}{self.cur_video_name}-trimmed{self.cur_video_extension}'
    
    def abort(self) -> None:
        for proc in psutil.process_iter():
            if 'ffmpeg' in proc.name():
                p = psutil.Process(proc.pid)
                p.kill()

                try:
                    os.remove('TEMP')
                    print('Cleaned up temp files.')
                except:
                    pass

                self.compressing = False
                self.trimming = False
                self.trimmed = False

                print('Aborting.')
    
    def help(self) -> None:
        sg.popup("Resolution: Set your video's dimensions (width x height).\n\nTarget File Size: Set the targetted file size for your video.\n\nAudio Bitrate: Set your video's audio bitrate.\n\nFramerate: Set your video's fps.\n\nFile Extension: Set the file type of your video.\n\nTrim: The first box is your video's initial start time, the second box is the duration afterwards.\n\nEnable Trim: Must be enabled to trim your video.\n\nRemove Audio: Self explanitory.\n\nUse H.265 Codec: Set your video to use the H.265 codec for a higher quality output. If you plan on sharing your video on Discord then do NOT use this option, it will not embed.\n\nPortrait Mode: Flips the set width and height resolution to output verticle videos correctly. If you've already manually set the resolution to vertical dimensions then this option is ignored.")

    def ui(self) -> None:
        # sg.change_look_and_feel('DarkAmber1')
        self.window = sg.Window(f"{self.author}'s Video Compressor", self.layout, resizable=False, finalize=True, element_justification='center')
        self.window['col_left'].expand(True, True, True)
        self.window['col_right'].expand(True, True, True)

        if not validate_ffmpeg():
            if platform.system() == 'Windows':
                sg.popup("Couldn't locate FFmpeg.\nThe app will fetch it for you, please close this window to begin.")
            else:
                sg.popup("Couldn't locate FFmpeg, please install it before continuing.")

            install_ffmpeg()

        while True:
            event, values, = self.window.read(timeout=1)
            # print(event, values)

            if event in (sg.WIN_CLOSED, 'Exit', 'Cancel'):
                self.abort()
                sys.exit()

            if event == 'select_videos':
                self.selected_videos = list_videos(values['select_videos'])

            if event == 'start':
                self.apply_options(values)
                self.start()
            
            if event == 'abort':
                self.abort()
            
            if event == 'help':
                self.help()

app = App()
