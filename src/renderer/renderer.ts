import { ipcRenderer, shell } from "electron";

const btnCompress: HTMLButtonElement = document.getElementById("btn-compress") as HTMLButtonElement;
const btnAbort: HTMLButtonElement = document.getElementById("btn-abort") as HTMLButtonElement;
const btnSupport: HTMLButtonElement = document.getElementById("btn-support") as HTMLButtonElement;
const btnGithub: HTMLButtonElement = document.getElementById("btn-github") as HTMLButtonElement;
const lblStatus: HTMLElement = document.getElementById("lbl-status") as HTMLElement;
const dropZone: HTMLElement = document.getElementById("drop-zone") as HTMLElement;
const progressBar: HTMLProgressElement = document.getElementById("progress-bar") as HTMLProgressElement;
const checkRemoveAudio: HTMLInputElement = document.getElementById("check-remove-audio") as HTMLInputElement;
const inputFileSize: HTMLInputElement = document.getElementById("input-file-size") as HTMLInputElement;

let videoPaths: string[] = [];

btnCompress?.addEventListener("click", () => {
	const removeAudio = checkRemoveAudio.checked;
	const fileSize = parseFloat(inputFileSize.value) || 8.0;
	btnCompress.disabled = true;
	ipcRenderer.send("requestCompress", removeAudio, fileSize);
});

btnAbort?.addEventListener("click", () => {
	ipcRenderer.send("requestAbort");
});

btnSupport?.addEventListener("click", () => {
	shell.openExternal("https://ko-fi.com/bigslime");
});

btnGithub?.addEventListener("click", () => {
	shell.openExternal("https://github.com/big-slime/video-compressor");
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

	lblStatus.innerText = `${videoPaths.length} video(s) ready to compress.`;
	btnCompress.disabled = false;
	ipcRenderer.send("droppedVideos", videoPaths);
});

ipcRenderer.on("statusUpdate", (event, msg: string) => {
	lblStatus.innerText = msg;
});

ipcRenderer.on("progressUpdate", (event, currentValue: number, totalValue: number) => {
	const progress = (currentValue / totalValue) * 100;
	console.log(`Progress: ${progress}`);
	progressBar.style.width = `${progress}%`;
});

ipcRenderer.on("compressionStart", (event) => {
	lblStatus.innerText = "Compressing, please wait...";
	btnCompress.disabled = true;
	btnAbort.disabled = false;
	checkRemoveAudio.disabled = true;
	inputFileSize.disabled = true;
	progressBar.style.width = "0%";
});

ipcRenderer.on("compressionComplete", (event) => {
	lblStatus.innerText = "Compression complete, enjoy!\nPlease consider suppporting me.";
	btnCompress.disabled = true;
	btnAbort.disabled = true;
	checkRemoveAudio.disabled = false;
	inputFileSize.disabled = false;
	progressBar.style.width = "100%";
});

ipcRenderer.on("compressionError", (event, err) => {
	lblStatus.innerText = err;
	btnCompress.disabled = true;
	btnAbort.disabled = true;
	checkRemoveAudio.disabled = false;
	inputFileSize.disabled = false;
	progressBar.style.width = "100%";
});
