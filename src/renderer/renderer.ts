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
const inputFileSize: HTMLInputElement = document.getElementById("input-file-size") as HTMLInputElement;

let videoPaths: string[] = [];
let compressing: boolean = false;

btnCompress?.addEventListener("click", () => {
	const removeAudio = checkRemoveAudio.checked;
	const h265 = checkH265.checked;
	const fileSize = parseFloat(inputFileSize.value) || 8.0;
	btnCompress.disabled = true;
	ipcRenderer.send("requestCompress", removeAudio, h265, fileSize);
});

btnAbort?.addEventListener("click", () => {
	ipcRenderer.send("requestAbort");
});

btnGithub?.addEventListener("click", () => {
	shell.openExternal("https://github.com/cheezos/video-compressor");
});

dropZone?.addEventListener("dragover", (event) => {
	if (compressing) return

	event.stopPropagation();
	event.preventDefault();
});

dropZone?.addEventListener("drop", (event) => {
	if (compressing) return

	event.stopPropagation();
	event.preventDefault();

	videoPaths = [];
	const files: FileList = event.dataTransfer?.files as FileList;

	for (const file of files) {
		videoPaths.push(file.path);
	}

	let text = `${videoPaths.length} videos ready!`;

	if (videoPaths.length < 2) {
		text = `1 video ready!`;
	}

	lblStatus.innerText = text;
	lblStatusSmall.innerText = "Click 'Compress' to begin.";
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
	lblStatusSmall.innerText = "Large videos can take a long time.";
	btnCompress.disabled = true;
	btnAbort.disabled = false;
	checkRemoveAudio.disabled = true;
	checkH265.disabled = true;
	inputFileSize.disabled = true;
	progressBar.style.width = "0%";
	compressing = true
});

ipcRenderer.on("compressionComplete", (event) => {
	lblStatus.innerText = "Compression complete!";
	lblStatusSmall.innerText = "Your compressed videos are now available.";
	btnCompress.disabled = true;
	btnAbort.disabled = true;
	checkRemoveAudio.disabled = false;
	checkH265.disabled = false;
	inputFileSize.disabled = false;
	progressBar.style.width = "100%";
	compressing = false
});

ipcRenderer.on("compressionError", (event, err) => {
	lblStatus.innerText = "Compression aborted!";
	lblStatusSmall.innerText = "Drop your videos here and try again.";
	btnCompress.disabled = true;
	btnAbort.disabled = true;
	checkRemoveAudio.disabled = false;
	checkH265.disabled = false;
	inputFileSize.disabled = false;
	progressBar.style.width = "100%";
	compressing = false
});
