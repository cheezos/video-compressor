# Created by Peb
# https://github.com/pebfromweb/Pebs-Video-Compressor
# Python 3.8.5 64-bit

import platform
import os
import subprocess
from tkinter import font
import PySimpleGUI as sg
from PySimpleGUI.PySimpleGUI import TITLE_LOCATION_BOTTOM

from utils import log


class App:
    def __init__(self) -> None:
        self.version = 'v3.0.0'
        self.author = 'Peb'
        self.github = 'https://github.com/pebfromweb/Pebs-Video-Compressor'
        self.os = platform.system()
        self.ffmpeg_installed = False
        self.msg = ''

        # Options
        self.selected_videos = []
        self.cur_queue = 0
        self.cur_pass = 0
        self.cur_video_length = 0.0
        self.cur_video_progress_s = 0.0
        self.cur_video_progress_percent = 0

        # Layout
        options_column_left = [
            [sg.Text('Resolution', font='Arial 12')],
            [sg.Text('Target File Size', font='Arial 12')],
            [sg.Text('Framerate', font='Arial 12')],
            [sg.Text('File Extension', font='Arial 12')],
            [sg.Text('Remove Audio', font='Arial 12')],
            [sg.Text('Use H.265 Codec', font='Arial 12')],
            [sg.Text('Portrait Mode', font='Arial 12')]
        ]

        options_column_right = [
            [sg.Input('1280', font='Arial 12', key='res_w', size=(5, 1)), sg.Text('W'), sg.Input('720', key='res_h', size=(5, 1)), sg.Text('H')],
            [sg.Input('8', font='Arial 12', key='file_size', size=(5, 1)), sg.Text('MB')],
            [sg.Input('30', font='Arial 12', key='framerate', size=(5, 1)), sg.Text('FPS')],
            [sg.Input('mp4', font='Arial 12', key='extension', size=(5, 1))],
            [sg.Checkbox('', font='Arial 12', default=False, key='remove_audio', change_submits=True)],
            [sg.Checkbox('', font='Arial 12', default=False, key='h265', change_submits=True)],
            [sg.Checkbox('', font='Arial 12', default=False, key='portrait', change_submits=True)]
        ]

        self.layout = [
            [sg.Text("Peb's Video Compressor " + self.version, font='Arial 16 bold', justification='center')],
            [sg.Text('', pad=(0,0), key='col_left'), sg.Column(options_column_left, vertical_alignment='right', element_justification='right', k='l'), 
             sg.VerticalSeparator(pad=None),
             sg.Text('', pad=(0,0), key='col_right'), sg.Column(options_column_right, vertical_alignment='left', element_justification='left', k='r')]
        ]

        # title = sg.T("Peb's Video Compressor " + self.version, font='Arial 14 bold')
        # resolution = sg.T('Resolution', font='Arial 12 bold'), sg.Input('1280', key='res_w', size=(5, 1)), sg.T('W'), sg.Input('720', key='res_h', size=(5, 1)), sg.T('H')

        # title_layout = [[title], [resolution]]
        # title_frame = sg.Frame(title='', layout=title_layout, border_width=1, element_justification='center')
        # title_frame.append(title)

        # self.layout = [title_frame]
        # self.layout = [[sg.T("Peb's Video Compressor " + self.version, size=(64, 1), justification='center', font='Arial 14 bold')],
        #                [sg.T('Resolution', font='Arial 12 bold'), sg.Input('1280', key='res_w', size=(5, 1)), sg.T('W'), sg.Input('720', key='res_h', size=(5, 1)), sg.T('H')],
        #                [sg.T('Target File Size', font='Arial 12 bold'), sg.Input('8', key='file_size', size=(5, 1))],
        #                [sg.T('Select video(s)', font='Arial 12 bold'), sg.Input(key = 'videos', change_submits = True), sg.FilesBrowse()]]

        self.create_window()

    def get_ffmpeg(self) -> bool:
        if not self.os == 'Windows':
            p = subprocess.Popen(
                'which ffmpeg', stdout=subprocess.PIPE, shell=True)
            result = p.stdout.readline()

            if result:
                self.msg = log('Found ffmpeg.')
                return True
            else:
                sg.popup(
                    'FFmpeg was not detected on your system, please install using your package manager.')
        else:
            if os.path.exists(os.getcwd() + '/FFmpeg/ffmpeg.exe') and os.path.exists(os.getcwd() + '/FFmpeg/ffprobe.exe'):
                self.msg = log('Found ffmpeg')
                return True
            else:
                self.install_ffmpeg()
                sg.popup(
                    'Installing FFmpeg, please wait.\nYou may close this window.')

        self.msg = log('Could not find ffmpeg.')
        return False

    def install_ffmpeg(self) -> None:
        if self.os == 'Windows':
            if not os.path.exists(os.getcwd() + '/FFmpeg'):
                os.mkdir(os.getcwd() + '/FFmpeg')
                self.msg = log('FFmpeg directory created.')

    def create_window(self) -> None:
        # sg.theme('SystemDefault1')
        self.window = sg.Window("Peb's Video Compressor", self.layout, resizable=True, finalize=True)
        self.window['l'].expand(True, True, True)
        self.window['r'].expand(True, True, True)
        self.window['col_left'].expand(True, True, True)
        self.window['col_right'].expand(True, True, True)
        self.ffmpeg_installed = self.get_ffmpeg()
        self.loop()

    def list_videos(self, str) -> list:
        vids = str.split(';')
        return vids

    def loop(self) -> None:
        while True:
            event, values, = self.window.read()

            if event in (sg.WIN_CLOSED, 'Exit', 'Cancel'):
                break
            else:
                # self.selected_videos = self.list_videos(values['videos'])
                pass

        self.window.close()


app = App()
