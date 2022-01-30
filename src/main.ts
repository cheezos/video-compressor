import { app, BrowserWindow, ipcMain, Notification } from "electron";
import { getFFmpeg, getVideoData, getVideoDuration, getCalculatedVideoBitrate } from "./utils";
import FfmpegCommand from "fluent-ffmpeg";

export let mainWindow: BrowserWindow;
let videoData: { base: string; path: string; name: string; ext: string }[] = [];
let currentIndex: number = 0;
let currentProgress: number = 1;
let totalProgress: number = 1;
let cmd: any = null;

app.on("ready", () => {
	mainWindow = new BrowserWindow({
		width: 350,
		height: 415,
		webPreferences: {
			contextIsolation: false,
			nodeIntegration: true,
			preload: __dirname + "/preload.js",
		},
		show: false,
		resizable: false,
		autoHideMenuBar: true,
	});

	mainWindow.loadFile("./index.html");

	mainWindow.on("ready-to-show", () => {
		mainWindow.show();

		getFFmpeg();
	});

	console.log("Window ready");
});

app.on("window-all-closed", () => {
	if (process.platform !== "darwin") {
		killFFmpeg();
		app.quit();
	}
});

ipcMain.on("droppedVideos", (event, vids: string[]) => {
	videoData = getVideoData(vids);
});

ipcMain.on("requestCompress", (event, removeAudio: boolean, h265: boolean, minBitrate: number, targetFileSize: number) => {
	currentIndex = 0;
	currentProgress = 0;

	compressQueue(mainWindow, videoData, removeAudio, h265, minBitrate, targetFileSize)
		.then(() => {
			event.reply("compressionComplete");
			new Notification({ title: "Compression complete", body: "Your new videos are located in the same directory" }).show();
		})
		.catch((err) => {
			event.reply("compressionError", err);
			new Notification({ title: "Error", body: "There was an error during compression" }).show();
		});
});

ipcMain.on("requestAbort", (event) => {
	killFFmpeg();
});

export function compressQueue(
	window: BrowserWindow,
	videoData: { base: string; path: string; name: string; ext: string }[],
	removeAudio: boolean,
	h265: boolean,
	minBitrate: number,
	targetFileSize: number
): Promise<boolean> {
	return new Promise<boolean>((resolve, reject) => {
		window.webContents.send("compressionStart");
		totalProgress = videoData.length * 2;

		const compress = () => {
			console.log(`Compressing ${currentIndex + 1}/${videoData.length}...`);

			getVideoDuration(videoData[currentIndex].base)
				.then((duration: number) => {
					const bitrate = getCalculatedVideoBitrate(duration, minBitrate, targetFileSize);

					compressVideo(window, videoData[currentIndex], bitrate, removeAudio, h265)
						.then(() => {
							if (currentIndex + 1 < videoData.length) {
								currentIndex += 1;
								compress();
							} else {
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

function compressVideo(
	window: BrowserWindow,
	videoData: { base: string; path: string; name: string; ext: string },
	bitrate: number,
	removeAudio: boolean,
	h265: boolean
): Promise<boolean> {
	return new Promise<boolean>((resolve, reject) => {
		cmd = FfmpegCommand();

		let audioArg = "-b:a 128k";
		let codec = "-c:v libx264";

		if (removeAudio) {
			audioArg = "-an";
		}

		if (h265) {
			codec = "-c:v libx265";
		}

		let pass1 = [`-y`, codec, `-b:v ${bitrate}k`, `-pass 1`, `-an`, `-f mp4`];
		let pass2 = [codec, `-b:v ${bitrate}k`, `-pass 2`, `-c:a aac`, audioArg];

		cmd.setFfmpegPath(getFFmpeg()[0]);
		cmd.setFfprobePath(getFFmpeg()[1]);
		cmd.input(videoData.base);
		cmd.outputOptions(pass1);
		cmd.output(`${videoData.path}temp`);

		cmd.on("end", () => {
			currentProgress += 1;
			window.webContents.send("progressUpdate", currentProgress, totalProgress);

			cmd = FfmpegCommand();
			cmd.setFfmpegPath(getFFmpeg()[0]);
			cmd.setFfprobePath(getFFmpeg()[1]);
			cmd.input(videoData.base);
			cmd.outputOptions(pass2);
			cmd.output(`${videoData.path}${videoData.name}-compressed${videoData.ext}`);

			cmd.on("end", () => {
				currentProgress += 1;
				window.webContents.send("progressUpdate", currentProgress, totalProgress);

				console.log(`Compressed ${videoData.name}`);
				resolve(true);
			});

			cmd.on("error", (err: any) => {
				reject(err);
			});

			cmd.run();
		});

		cmd.on("error", (err: any) => {
			reject(err);
		});

		cmd.run();
	});
}

function killFFmpeg(): void {
	if (cmd != null) {
		cmd.kill();
		console.log("Killed FFmpeg process");
	}
}
