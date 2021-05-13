# Created by Colt
# https://github.com/colthub/video-compressor
# Python 3.8.5 64-bit

import platform
import os
import subprocess
import PySimpleGUI as sg

from utils import validate_ffmpeg, list_videos, remove_extension, get_extension, get_ffmpeg, calculate_video_bitrate

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
        self.trim_s = '00:00:00'
        self.trim_e = '00:00:10'
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
            [sg.Text('Trim Length', font=self.font_small)],
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
            [sg.Output(size=(60, 10), key='output')],
            [sg.Button('Start', key='start'), sg.Button('Abort')]
        ]

        self.create_window()

    def install_ffmpeg(self) -> None:
        if self.os == 'Windows':
            if not os.path.exists(os.getcwd() + '/FFmpeg'):
                os.mkdir(os.getcwd() + '/FFmpeg')
                self.msg = print('FFmpeg directory created.')

    def create_window(self) -> None:
        # sg.theme('SystemDefault1')
        self.window = sg.Window(f"{self.author}'s Video Compressor", self.layout, resizable=False, finalize=True, element_justification='center')
        self.window['col_left'].expand(True, True, True)
        self.window['col_right'].expand(True, True, True)
        if not validate_ffmpeg(): sg.popup("Couldn't detect FFmpeg on your computer!")
        self.loop()

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
        self.file_extension = values['extension']
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
        if not self.selected_videos or len(self.selected_videos) == 0:
            print('No videos selected!')
        else:
            if not self.compressing and not self.trimming:
                self.get_video_data(self.selected_videos[self.cur_queue])

                if self.enable_trim and not self.trimmed:
                    self.trim()
                else:
                    self.compress()
            
            while (self.trimming):
                line = str(self.proc.stdout.readline())

                if self.proc.poll() or any(x in line for x in ['', 'failed']):
                    self.trimming = False
                    self.trimmed = True
                    print('Trimming complete.')
                    self.start()
            
            while (self.compressing):
                line = str(self.proc.stdout.readline())

                if self.proc.poll() or any(x in line for x in ['', 'failed']):
                    self.compressing = False
                    # self.cur_queue += 1
                    print('Compression complete.')
                    # self.start()

    def trim(self) -> None:
        input = f'-i "{self.cur_video}"'
        trim_start = f'-ss {self.trim_s}'
        trim_end = f'-t {self.trim_e}'
        output = f'"{self.cur_video_trimmed}"'

        cmd = f'{self.ffmpeg} -y {trim_start} {input} {trim_end} {output}'
        if not self.trimming: self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

        self.trimming = True

        print(f'Trimming {self.cur_video} from {self.trim_s} to {self.trim_e}, please wait...')

    def compress(self):
        if self.trimmed:
            self.cur_video = self.cur_video_trimmed

            print(f'Using trimmed version: {self.cur_video_trimmed}')

        input = f'-i "{self.cur_video}"'
        codec = '-c:v libx265' if self.use_h265 else '-c:v libx264'
        video_bitrate = f'-b:v {calculate_video_bitrate(self.cur_video, self.target_file_size, self.audio_bitrate)}k'
        audio_bitrate = f'-c:a aac -b:a {self.audio_bitrate}k' if not self.remove_audio else '-an'
        fps = f'-r {self.fps}'
        resolution = f'-vf scale={self.res_w}:{self.res_h}'
        output = f'{self.cur_video_path}{self.cur_video_name}-compressed{self.cur_video_extension}'

        cmd = f'{self.ffmpeg} -y {input} {codec} {video_bitrate} {fps} {resolution} -pass 1 -an -f mp4 TEMP && {self.ffmpeg} -y {input} {codec} {video_bitrate} {fps} {resolution} -pass 2 {audio_bitrate} {output}'
        if not self.compressing: self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

        self.compressing = True
        
        print(f'Compressing video {self.cur_queue + 1}/{len(self.selected_videos)}, please wait...')

    def get_video_data(self, video):
        self.cur_video = video
        self.cur_video_name = remove_extension(self.cur_video)
        self.cur_video_path = self.cur_video.split(self.cur_video_name)[0]
        self.cur_video_extension = get_extension(self.cur_video)
        self.cur_video_trimmed = f'{self.cur_video_path}{self.cur_video_name}-trimmed{self.cur_video_extension}'

    def loop(self) -> None:
        while True:
            event, values, = self.window.read()
            # print(event)

            if event in (sg.WIN_CLOSED, 'Exit', 'Cancel'):
                break

            if event == 'select_videos':
                self.selected_videos = list_videos(values['select_videos'])

            if event == 'start':
                self.apply_options(values)
                self.start()

        self.window.close()


app = App()
