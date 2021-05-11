# Created by Peb
# https://github.com/pebfromweb/Pebs-Video-Compressor
# Python 3.8.5 64-bit

import platform
import os
import subprocess
import PySimpleGUI as sg
from datetime import datetime


class App:
    def __init__(self) -> None:
        self.version = 'v3.0.0'
        self.author = 'Peb'
        self.github = 'https://github.com/pebfromweb/Pebs-Video-Compressor'
        self.os = platform.system()
        self.ffmpeg_installed = False
        self.msg = ''
        self.selected_videos = []

        self.layout = [[sg.Text("Peb's Video Compressor " + self.version, size=(64, 1))],
                       [sg.Text(self.github, size=(64, 1))],

                       ]

        self.create_window()

    def get_ffmpeg(self) -> bool:
        if not self.os == 'Windows':
            p = subprocess.Popen(
                'which ffmpeg', stdout=subprocess.PIPE, shell=True)
            result = p.stdout.readline()

            if result:
                self.update('Found ffmpeg.')
                return True
            else:
                sg.popup(
                    'FFmpeg was not detected on your system, please install using your package manager.')
        else:
            if os.path.exists(os.getcwd() + '/FFmpeg/ffmpeg.exe') and os.path.exists(os.getcwd() + '/FFmpeg/ffprobe.exe'):
                self.update('Found ffmpeg')
                return True
            else:
                self.install_ffmpeg()
                sg.popup(
                    'Installing FFmpeg, please wait.\nYou may close this window.')

        self.update('Could not find ffmpeg.')
        return False

    def install_ffmpeg(self) -> None:
        if self.os == 'Windows':
            if not os.path.exists(os.getcwd() + '/FFmpeg'):
                os.mkdir(os.getcwd() + '/FFmpeg')
                self.update('FFmpeg directory created.')

    def create_window(self) -> None:
        # sg.theme('SystemDefault1')
        self.window = sg.Window("Peb's Video Compressor", self.layout)
        self.ffmpeg_installed = self.get_ffmpeg()
        self.loop()

    def update(self, msg) -> None:
        self.msg = msg
        print('PVC: ' + msg)

    def loop(self) -> None:
        while True:
            event, values, = self.window.read()
            print(event, values)

            if event in (sg.WIN_CLOSED, 'Exit', 'Cancel'):
                break

        self.window.close()


app = App()
