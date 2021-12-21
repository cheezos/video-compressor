import { ipcRenderer } from "electron";

const btnCompress: HTMLButtonElement = document.getElementById("btn-compress") as HTMLButtonElement;
const btnAbort: HTMLButtonElement = document.getElementById("btn-abort") as HTMLButtonElement;
const lblStatus: HTMLElement = document.getElementById("lbl-status") as HTMLElement;
const dropZone: HTMLElement = document.getElementById("drop-zone") as HTMLElement;
const progressBar: HTMLProgressElement = document.getElementById("progress-bar") as HTMLProgressElement;
const checkRemoveAudio: HTMLElement = document.getElementById("check-remove-audio") as HTMLElement;
const editFileSize: HTMLElement = document.getElementById("edit-file-size") as HTMLElement;

let videoPaths: string[] = [];

btnCompress?.addEventListener("click", () => {
	btnCompress.disabled = true;
	ipcRenderer.send("requestCompress");
});

btnAbort?.addEventListener("click", () => {
	ipcRenderer.send("requestAbort");
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
	progressBar.style.width = "0%";
});

ipcRenderer.on("compressionComplete", (event) => {
	lblStatus.innerText = "Compression complete.";
	btnCompress.disabled = true;
	btnAbort.disabled = true;
});

ipcRenderer.on("compressionError", (event, err) => {
	lblStatus.innerText = `An error occured:\n${err}`;
	btnCompress.disabled = true;
	btnAbort.disabled = true;
});
