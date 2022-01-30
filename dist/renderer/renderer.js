"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const btnCompress = document.getElementById("btn-compress");
const btnAbort = document.getElementById("btn-abort");
const btnSupport = document.getElementById("btn-support");
const btnGithub = document.getElementById("btn-github");
const lblStatus = document.getElementById("lbl-status");
const lblStatusSmall = document.getElementById("lbl-status-small");
const dropZone = document.getElementById("drop-zone");
const progressBar = document.getElementById("progress-bar");
const checkRemoveAudio = document.getElementById("check-remove-audio");
const checkH265 = document.getElementById("check-h265");
const inputMinBitrate = document.getElementById("input-min-bitrate");
const inputFileSize = document.getElementById("input-file-size");
let videoPaths = [];
btnCompress?.addEventListener("click", () => {
    const removeAudio = checkRemoveAudio.checked;
    const h265 = checkH265.checked;
    const minBitrate = parseFloat(inputMinBitrate.value) || 100;
    const fileSize = parseFloat(inputFileSize.value) || 8.0;
    btnCompress.disabled = true;
    electron_1.ipcRenderer.send("requestCompress", removeAudio, h265, minBitrate, fileSize);
});
btnAbort?.addEventListener("click", () => {
    electron_1.ipcRenderer.send("requestAbort");
});
btnSupport?.addEventListener("click", () => {
    electron_1.shell.openExternal("https://ko-fi.com/slugnasty");
});
btnGithub?.addEventListener("click", () => {
    electron_1.shell.openExternal("https://github.com/slugnasty/video-compressor");
});
dropZone?.addEventListener("dragover", (event) => {
    event.stopPropagation();
    event.preventDefault();
});
dropZone?.addEventListener("drop", (event) => {
    event.stopPropagation();
    event.preventDefault();
    videoPaths = [];
    const files = event.dataTransfer?.files;
    for (const file of files) {
        videoPaths.push(file.path);
    }
    lblStatus.innerText = `${videoPaths.length} video(s) ready to compress`;
    lblStatusSmall.innerText = "Click 'Compress' to begin";
    btnCompress.disabled = false;
    electron_1.ipcRenderer.send("droppedVideos", videoPaths);
});
electron_1.ipcRenderer.on("message", (event, bigText, smallText) => {
    lblStatus.innerText = bigText;
    if (smallText) {
        lblStatusSmall.innerText = smallText;
    }
});
electron_1.ipcRenderer.on("progressUpdate", (event, currentValue, totalValue) => {
    const progress = Math.round((currentValue / totalValue) * 100);
    console.log(`Progress: ${progress}`);
    lblStatusSmall.innerText = `Progress: ${progress}%`;
    progressBar.style.width = `${progress}%`;
});
electron_1.ipcRenderer.on("compressionStart", (event) => {
    lblStatus.innerText = "Compressing, please wait...";
    lblStatusSmall.innerText = "Large videos can take a long time!";
    btnCompress.disabled = true;
    btnAbort.disabled = false;
    checkRemoveAudio.disabled = true;
    checkH265.disabled = true;
    inputMinBitrate.disabled = true;
    inputFileSize.disabled = true;
    progressBar.style.width = "0%";
});
electron_1.ipcRenderer.on("compressionComplete", (event) => {
    lblStatus.innerText = "Compression complete";
    lblStatusSmall.innerText = "Your new videos are located in the same directory";
    btnCompress.disabled = true;
    btnAbort.disabled = true;
    checkRemoveAudio.disabled = false;
    checkH265.disabled = false;
    inputMinBitrate.disabled = false;
    inputFileSize.disabled = false;
    progressBar.style.width = "100%";
});
electron_1.ipcRenderer.on("compressionError", (event, err) => {
    lblStatus.innerText = "Aborted compression";
    lblStatusSmall.innerText = "Drop your videos here and try again";
    btnCompress.disabled = true;
    btnAbort.disabled = true;
    checkRemoveAudio.disabled = false;
    checkH265.disabled = false;
    inputMinBitrate.disabled = false;
    inputFileSize.disabled = false;
    progressBar.style.width = "100%";
});
