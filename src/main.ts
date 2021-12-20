import { app, BrowserWindow, ipcMain } from "electron";
import electronReload from "electron-reload";
import { getVideoData, compressQueue } from "./utils";

electronReload(__dirname, {});

let mainWindow: BrowserWindow;
let videoData: { base: string; path: string; name: string; ext: string }[] = [];

app.on("ready", () => {
	mainWindow = new BrowserWindow({
		width: 400,
		height: 300,
		webPreferences: {
			contextIsolation: false,
			nodeIntegration: true,
			preload: __dirname + "/preload.js",
		},
		show: false,
		resizable: false,
	});

	mainWindow.loadFile("./index.html");

	mainWindow.on("ready-to-show", () => {
		mainWindow.show();
	});

	console.log("Window ready.");
});

ipcMain.on("droppedVideos", (event, vids) => {
	videoData = getVideoData(vids);
});

ipcMain.on("requestCompress", (event) => {
	event.reply("compressionStart");

	compressQueue(videoData)
		.then(() => {
			event.reply("compressionComplete");
		})
		.catch((err) => {
			event.reply("compressionError", err);
		});
});
