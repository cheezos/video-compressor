"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getFFmpeg = exports.getCalculatedVideoBitrate = exports.getVideoDuration = exports.getVideoData = void 0;
const electron_1 = require("electron");
const path_1 = require("path");
const child_process_1 = require("child_process");
const fluent_ffmpeg_1 = __importDefault(require("fluent-ffmpeg"));
function getVideoData(videoPaths) {
    let videoData = [];
    for (let base of videoPaths) {
        const name = (0, path_1.parse)(base).name;
        const ext = (0, path_1.parse)(base).ext;
        const path = base.split(name)[0];
        videoData.push({ base: base, path: path, name: name, ext: ext });
    }
    return videoData;
}
exports.getVideoData = getVideoData;
function getVideoDuration(videoPath) {
    return new Promise((resolve, reject) => {
        const cmd = (0, fluent_ffmpeg_1.default)();
        cmd.setFfmpegPath(getFFmpeg()[0]);
        cmd.setFfprobePath(getFFmpeg()[1]);
        cmd.input(videoPath);
        cmd.ffprobe((err, metadata) => {
            if (err) {
                reject(err);
            }
            else {
                const duration = metadata.format.duration;
                console.log(`Video duration: ${duration}`);
                resolve(duration);
            }
        });
    });
}
exports.getVideoDuration = getVideoDuration;
function getCalculatedVideoBitrate(duration, targetFileSize) {
    const magic = Math.max((targetFileSize * 8192.0) / (1.048576 * duration) - 128, 100);
    console.log(`Calculated bitrate: ${magic}`);
    return magic;
}
exports.getCalculatedVideoBitrate = getCalculatedVideoBitrate;
function getFFmpeg() {
    let ffmpegPath = __dirname + "/ffmpeg.exe";
    let ffprobePath = __dirname + "/ffprobe.exe";
    if (process.platform === "linux") {
        const cmd = (0, child_process_1.spawnSync)("which", ["ffmpeg"], { encoding: "utf8" });
        if (cmd.stdout != "") {
            ffmpegPath = "ffmpeg";
            ffprobePath = "ffprobe";
        }
        else {
            require("./main").mainWindow.webContents.send("message", "FFmpeg missing!", "Please install FFmpeg before continuing");
            new electron_1.Notification({ title: "FFmpeg missing!", body: "Please install FFmpeg before continuing" }).show();
            ffmpegPath = "null";
            ffprobePath = "null";
        }
    }
    return [ffmpegPath, ffprobePath];
}
exports.getFFmpeg = getFFmpeg;
