# Created by Colt
# https://github.com/colthub/video-compressor
# Python 3.8.5 64-bit

import platform
import os
import subprocess
import PySimpleGUI as sg

from utils import log, list_videos, remove_extension, get_extension


class App:
    def __init__(self) -> None:
        self.version = 'v3.0.0'
        self.author = 'Colt'
        self.github = 'github.com/colthub/video-compressor'
        self.os = platform.system()
        self.ffmpeg_installed = False
        self.compressing = False
        self.trimming = False
        self.proc = ''

        # UI Preferences
        self.font_large = 'Arial 14 bold'
        self.font_small = 'Arial 12'

        # Options
        self.res_w = 1280
        self.res_h = 720
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

        self.ffmpeg = 'ffmpeg' if self.os == 'Linux' else os.getcwd() + '\FFmpeg\ffmpeg.exe'
        self.ffprobe = 'ffprobe' if self.os == 'Linux' else os.getcwd() + '\FFmpeg\ffprobe.exe'

        # Layout
        options_column_left = [
            [sg.Text('Resolution', font=self.font_small)],
            [sg.Text('Target File Size', font=self.font_small)],
            [sg.Text('Framerate', font=self.font_small)],
            [sg.Text('File Extension', font=self.font_small)],
            [sg.Text('Trim Length', font=self.font_small)],
            [sg.Text('Enable Trim', font=self.font_small)],
            [sg.Text('Remove Audio', font=self.font_small)],
            [sg.Text('Use H.265 Codec', font=self.font_small)],
            [sg.Text('Portrait Mode', font=self.font_small)]
        ]

        options_column_right = [
            [sg.Input('1280', font=self.font_small, key='res_w', size=(7, 1)), sg.Input( '720', key='res_h', font=self.font_small, size=(7, 1))],
            [sg.Input('8', font=self.font_small, key='file_size', size=(7, 1)), sg.Text('MB')],
            [sg.Input('30', font=self.font_small, key='framerate', size=(7, 1)), sg.Text('FPS')],
            [sg.Input('mp4', font=self.font_small, key='extension', size=(7, 1))], 
            [sg.Input(self.trim_s, font=self.font_small, key='trim_start', size=(7, 1)), sg.Input(self.trim_e, font=self.font_small, key='trim_end', size=(7, 1))], 
            [sg.Checkbox('', font=self.font_small, default=False, key='trim', change_submits=True)],
            [sg.Checkbox('', font=self.font_small, default=False, key='audio', change_submits=True)],
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
            [sg.Output(size=(60, 10))],
            [sg.Button('Compress', key='compress'), sg.Button('Abort')]
        ]

        self.create_window()

    def get_ffmpeg(self) -> bool:
        if not self.os == 'Windows':
            p = subprocess.Popen( 'which ffmpeg', stdout=subprocess.PIPE, shell=True)
            result = p.stdout.readline()

            if result:
                self.msg = log('Found ffmpeg.')
                return True
            else:
                sg.popup( 'FFmpeg was not detected on your system, please install using your package manager.')
        else:
            if os.path.exists(os.getcwd() + '/FFmpeg/ffmpeg.exe') and os.path.exists(os.getcwd() + '/FFmpeg/ffprobe.exe'):
                self.msg = log('Found ffmpeg')
                return True
            else:
                self.install_ffmpeg()
                sg.popup( 'Installing FFmpeg, please wait.\nYou may close this window.')

        self.msg = log('Could not find ffmpeg.')
        return False

    def install_ffmpeg(self) -> None:
        if self.os == 'Windows':
            if not os.path.exists(os.getcwd() + '/FFmpeg'):
                os.mkdir(os.getcwd() + '/FFmpeg')
                self.msg = log('FFmpeg directory created.')

    def create_window(self) -> None:
        # sg.theme('SystemDefault1')
        self.window = sg.Window(f"{self.author}'s Video Compressor", self.layout, resizable=False, finalize=True, element_justification='center')
        self.window['col_left'].expand(True, True, True)
        self.window['col_right'].expand(True, True, True)
        self.ffmpeg_installed = self.get_ffmpeg()
        self.loop()

    def apply_options(self, values) -> None:
        self.res_w = int(values['res_w'])
        self.res_h = int(values['res_h'])
        log(f'Set resolution to {self.res_w} x {self.res_h}.')
        self.fps = float(values['framerate'])
        log(f'Set framerate to {self.fps}fps.')
        self.file_extension = values['extension']
        log(f'Set extension to {self.file_extension}.')
        self.trim_s = values['trim_start']
        self.trim_e = values['trim_end']
        self.enable_trim = values['trim']
        if self.enable_trim: log(f'Trimming video(s) from {self.trim_s} to {self.trim_e}.')
        self.remove_audio = values['audio']
        if self.remove_audio: log('Muting video(s).')
        self.use_h265 = values['h265']
        if self.use_h265: log('Using H.265 codec.')
        self.portrait_mode = values['portrait']
        if self.portrait_mode:
            if self.res_h < self.res_w:
                h = self.res_h
                self.res_h = self.res_w
                self.res_w = h
                log('Using portrait mode, switching resolution.')
            else:
                log('Using portrait mode.')

    def compress(self) -> None:
        if not self.selected_videos or len(self.selected_videos) == 0:
            log('No videos selected!')
        else:
            log(f'Compressing video {self.cur_queue + 1}/{len(self.selected_videos)}.')
            self.get_video_data(self.selected_videos[self.cur_queue])
            # x = subprocess.Popen( f'{self.ffprobe} -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video}"', stdout=subprocess.PIPE, shell=True)
            # orig_length = float(x.stdout.readline())
            print(self.cur_video, self.cur_video_path, self.cur_video_name, self.cur_video_extension)

            if self.enable_trim:
                # self.trim()
                pass
    
    def get_video_data(self, video):
        self.cur_video = video
        self.cur_video_name = remove_extension(self.cur_video)
        self.cur_video_path = self.cur_video.split(self.cur_video_name)[0]
        self.cur_video_extension = get_extension(self.cur_video)
    
    def trim(self) -> None:
        self.proc = subprocess.Popen( f'{self.ffmpeg} -ss {self.trim_s} -i "{video}" -t {self.trim_e} -vcodec copy -acodec copy "{path}{video_no_ext}-trimmed{extension}"', stdout=subprocess.PIPE, shell=True)
        print(self.proc.stdout.readline())
        self.trimming = True

    def loop(self) -> None:
        while True:
            event, values, = self.window.read()
            print(event)

            if self.compressing:
                self.window.refresh()
                print(self.proc.stdout.readline())

            if event in (sg.WIN_CLOSED, 'Exit', 'Cancel'):
                break

            if event == 'select_videos':
                self.selected_videos = list_videos(values['select_videos'])

            if event == 'compress':
                self.apply_options(values)
                self.compress()

        self.window.close()


app = App()
