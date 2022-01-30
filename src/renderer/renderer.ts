import { ipcRenderer, shell } from "electron";

const btnCompress: HTMLButtonElement = document.getElementById("btn-compress") as HTMLButtonElement;
const btnAbort: HTMLButtonElement = document.getElementById("btn-abort") as HTMLButtonElement;
const btnSupport: HTMLButtonElement = document.getElementById("btn-support") as HTMLButtonElement;
const btnGithub: HTMLButtonElement = document.getElementById("btn-github") as HTMLButtonElement;
const lblStatus: HTMLElement = document.getElementById("lbl-status") as HTMLElement;
const lblStatusSmall: HTMLElement = document.getElementById("lbl-status-small") as HTMLElement;
const dropZone: HTMLElement = document.getElementById("drop-zone") as HTMLElement;
const progressBar: HTMLProgressElement = document.getElementById("progress-bar") as HTMLProgressElement;
const checkRemoveAudio: HTMLInputElement = document.getElementById("check-remove-audio") as HTMLInputElement;
const checkH265: HTMLInputElement = document.getElementById("check-h265") as HTMLInputElement;
const inputMinBitrate: HTMLInputElement = document.getElementById("input-min-bitrate") as HTMLInputElement;
const inputFileSize: HTMLInputElement = document.getElementById("input-file-size") as HTMLInputElement;

let videoPaths: string[] = [];

btnCompress?.addEventListener("click", () => {
	const removeAudio = checkRemoveAudio.checked;
	const h265 = checkH265.checked;
	const minBitrate = parseFloat(inputMinBitrate.value) || 100;
	const fileSize = parseFloat(inputFileSize.value) || 8.0;
	btnCompress.disabled = true;
	ipcRenderer.send("requestCompress", removeAudio, h265, minBitrate, fileSize);
});

btnAbort?.addEventListener("click", () => {
	ipcRenderer.send("requestAbort");
});

btnSupport?.addEventListener("click", () => {
	shell.openExternal("https://ko-fi.com/slugnasty");
});

btnGithub?.addEventListener("click", () => {
	shell.openExternal("https://github.com/slugnasty/video-compressor");
});

dropZone?.addEventListener("dragover", (event) => {
	event.stopPropagation();
	event.preventDefault();
});

dropZone?.addEventListener("drop", (event) => {
	event.stopPropagation();
	event.preventDefault();

	videoPaths = [];
	const files: FileList = event.dataTransfer?.files as FileList;

	for (const file of files) {
		videoPaths.push(file.path);
	}

	lblStatus.innerText = `${videoPaths.length} video(s) ready to compress`;
	lblStatusSmall.innerText = "Click 'Compress' to begin";
	btnCompress.disabled = false;
	ipcRenderer.send("droppedVideos", videoPaths);
});

ipcRenderer.on("message", (event, bigText: string, smallText?: string) => {
	lblStatus.innerText = bigText;

	if (smallText) {
		lblStatusSmall.innerText = smallText;
	}
});

ipcRenderer.on("progressUpdate", (event, currentValue: number, totalValue: number) => {
	const progress = Math.round((currentValue / totalValue) * 100);
	console.log(`Progress: ${progress}`);
	lblStatusSmall.innerText = `Progress: ${progress}%`;
	progressBar.style.width = `${progress}%`;
});

ipcRenderer.on("compressionStart", (event) => {
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

ipcRenderer.on("compressionComplete", (event) => {
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

ipcRenderer.on("compressionError", (event, err) => {
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
