"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.compressQueue = exports.mainWindow = void 0;
const electron_1 = require("electron");
const utils_1 = require("./utils");
const fluent_ffmpeg_1 = __importDefault(require("fluent-ffmpeg"));
let videoData = [];
let currentIndex = 0;
let currentProgress = 1;
let totalProgress = 1;
let cmd = null;
electron_1.app.on("ready", () => {
    electron_1.app.setAppUserModelId("Bepto Video Compressor");
    exports.mainWindow = new electron_1.BrowserWindow({
        width: 310,
        height: 390,
        webPreferences: {
            contextIsolation: false,
            nodeIntegration: true,
            preload: __dirname + "/preload.js",
        },
        show: false,
        resizable: false,
        autoHideMenuBar: true,
    });
    exports.mainWindow.loadFile("./index.html");
    exports.mainWindow.on("ready-to-show", () => {
        exports.mainWindow.show();
        (0, utils_1.getFFmpeg)();
    });
    console.log("Window ready");
});
electron_1.app.on("window-all-closed", () => {
    if (process.platform !== "darwin") {
        killFFmpeg();
        electron_1.app.quit();
    }
});
electron_1.ipcMain.on("droppedVideos", (event, vids) => {
    videoData = (0, utils_1.getVideoData)(vids);
});
electron_1.ipcMain.on("requestCompress", (event, removeAudio, h265, targetFileSize) => {
    currentIndex = 0;
    currentProgress = 0;
    compressQueue(exports.mainWindow, videoData, removeAudio, h265, targetFileSize)
        .then(() => {
        event.reply("compressionComplete");
        new electron_1.Notification({ title: "Compression complete!" }).show();
    })
        .catch((err) => {
        event.reply("compressionError", err);
        new electron_1.Notification({ title: "Aborted!" }).show();
    });
});
electron_1.ipcMain.on("requestAbort", (event) => {
    killFFmpeg();
});
function compressQueue(window, videoData, removeAudio, h265, targetFileSize) {
    return new Promise((resolve, reject) => {
        window.webContents.send("compressionStart");
        totalProgress = videoData.length * 2;
        const compress = () => {
            console.log(`Compressing ${currentIndex + 1}/${videoData.length}...`);
            (0, utils_1.getVideoDuration)(videoData[currentIndex].base)
                .then((duration) => {
                const bitrate = (0, utils_1.getCalculatedVideoBitrate)(duration, targetFileSize);
                compressVideo(window, videoData[currentIndex], bitrate, removeAudio, h265)
                    .then(() => {
                    if (currentIndex + 1 < videoData.length) {
                        currentIndex += 1;
                        compress();
                    }
                    else {
                        resolve(true);
                    }
                })
                    .catch((err) => {
                    reject(err);
                });
            })
                .catch((err) => {
                reject(err);
            });
        };
        compress();
    });
}
exports.compressQueue = compressQueue;
function compressVideo(window, videoData, bitrate, removeAudio, h265) {
    return new Promise((resolve, reject) => {
        cmd = (0, fluent_ffmpeg_1.default)();
        let audio = "-b:a 128k";
        let codec = "-c:v libx264";
        if (removeAudio) {
            audio = "-an";
        }
        if (h265) {
            codec = "-c:v libx265";
        }
        let pass1 = [`-y`, codec, `-b:v ${bitrate}k`, `-r 24`, `-vf scale=-1:540`, `-pass 1`, `-an`, `-f mp4`];
        let pass2 = [codec, `-b:v ${bitrate}k`, `-r 24`, `-vf scale=-1:540`, `-pass 2`, `-c:a aac`, audio];
        cmd.setFfmpegPath((0, utils_1.getFFmpeg)()[0]);
        cmd.setFfprobePath((0, utils_1.getFFmpeg)()[1]);
        cmd.input(videoData.base);
        cmd.outputOptions(pass1);
        cmd.output(`${videoData.path}temp`);
        cmd.on("end", () => {
            currentProgress += 1;
            window.webContents.send("progressUpdate", currentProgress, totalProgress);
            cmd = (0, fluent_ffmpeg_1.default)();
            cmd.setFfmpegPath((0, utils_1.getFFmpeg)()[0]);
            cmd.setFfprobePath((0, utils_1.getFFmpeg)()[1]);
            cmd.input(videoData.base);
            cmd.outputOptions(pass2);
            cmd.output(`${videoData.path}${videoData.name}-compressed${videoData.ext}`);
            cmd.on("end", () => {
                currentProgress += 1;
                window.webContents.send("progressUpdate", currentProgress, totalProgress);
                electron_1.shell.openPath(videoData.path);
                console.log(`Compressed ${videoData.name}`);
                resolve(true);
            });
            cmd.on("error", (err) => {
                reject(err);
            });
            cmd.run();
        });
        cmd.on("error", (err) => {
            reject(err);
        });
        cmd.run();
    });
}
function killFFmpeg() {
    if (cmd != null) {
        cmd.kill();
        console.log("Killed FFmpeg process");
    }
}
