import { app, BrowserWindow, ipcMain } from "electron";
import { getVideoData, getVideoDuration, getCalculatedVideoBitrate } from "./utils";
import FfmpegCommand from "fluent-ffmpeg";

let mainWindow: BrowserWindow;
let videoData: { base: string; path: string; name: string; ext: string }[] = [];
let currentIndex: number = 0;
let currentProgress: number = 1;
let totalProgress: number = 1;

app.on("ready", () => {
	mainWindow = new BrowserWindow({
		width: 350,
		height: 425,
		webPreferences: {
			contextIsolation: false,
			nodeIntegration: true,
			preload: __dirname + "/preload.js",
		},
		show: false,
		// resizable: false,
	});

	mainWindow.loadFile("./index.html");
	mainWindow.webContents.openDevTools();

	mainWindow.on("ready-to-show", () => {
		mainWindow.show();
	});

	console.log("Window ready.");
});

ipcMain.on("droppedVideos", (event, vids: string[]) => {
	videoData = getVideoData(vids);
});

ipcMain.on("requestCompress", (event) => {
	currentIndex = 0;
	currentProgress = 0;

	compressQueue(mainWindow, videoData)
		.then(() => {
			event.reply("compressionComplete");
		})
		.catch((err) => {
			event.reply("compressionError", err);
		});
});

export function compressQueue(window: BrowserWindow, videoData: { base: string; path: string; name: string; ext: string }[]): Promise<boolean> {
	return new Promise<boolean>((resolve, reject) => {
		window.webContents.send("compressionStart");
		totalProgress = videoData.length * 2;

		const compress = () => {
			console.log(`Compressing ${currentIndex + 1}/${videoData.length}...`);

			getVideoDuration(videoData[currentIndex].base)
				.then((duration: number) => {
					const bitrate = getCalculatedVideoBitrate(duration);

					compressVideo(window, videoData[currentIndex], bitrate)
						.then(() => {
							// currentProgress += 1;

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

function compressVideo(window: BrowserWindow, videoData: { base: string; path: string; name: string; ext: string }, bitrate: number): Promise<boolean> {
	return new Promise<boolean>((resolve, reject) => {
		const cmd = FfmpegCommand();
		const input = videoData.base;

		cmd.setFfmpegPath(__dirname + "/ffmpeg.exe");
		cmd.setFfprobePath(__dirname + "/ffprobe.exe");

		const pass1 = [
			// pass 1
			`-y`,
			`-c:v libx264`,
			`-b:v ${bitrate}k`,
			`-pass 1`,
			`-an`,
			`-f mp4`,
		];

		const pass2 = [
			// pass 2
			`-c:v libx264`,
			`-b:v ${bitrate}k`,
			`-pass 2`,
			`-c:a aac`,
			`-b:a 128k`,
		];

		cmd.input(input);
		cmd.outputOptions(pass1);
		cmd.output(`${videoData.path}temp`);

		cmd.on("end", () => {
			currentProgress += 1;
			window.webContents.send("progressUpdate", currentProgress, totalProgress);

			const cmd = FfmpegCommand();
			cmd.setFfmpegPath(__dirname + "/ffmpeg.exe");
			cmd.setFfprobePath(__dirname + "/ffprobe.exe");

			cmd.input(input);
			cmd.outputOptions(pass2);
			cmd.output(`${videoData.path}${videoData.name}-compressed${videoData.ext}`);

			cmd.on("end", () => {
				currentProgress += 1;
				window.webContents.send("progressUpdate", currentProgress, totalProgress);

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
