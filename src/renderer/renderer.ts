import { ipcRenderer } from "electron";

const btnCompress: HTMLButtonElement = document.getElementById("btn-compress") as HTMLButtonElement;
const btnAbort: HTMLButtonElement = document.getElementById("btn-abort") as HTMLButtonElement;
const lblStatus: HTMLElement = document.getElementById("lbl-status") as HTMLElement;
const dropZone: HTMLElement = document.getElementById("drop-zone") as HTMLElement;

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

ipcRenderer.on("statusUpdate", (event, msg) => {
	lblStatus.innerText = msg;
});

ipcRenderer.on("compressionStart", (event) => {
	lblStatus.innerText = "Compressing, please wait...";
	btnCompress.disabled = true;
	btnAbort.disabled = false;
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
