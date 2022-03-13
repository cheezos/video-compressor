import { Notification } from "electron";
import { parse } from "path";
import { spawnSync } from "child_process";
import FfmpegCommand from "fluent-ffmpeg";

export function getVideoData(videoPaths: string[]): { base: string; path: string; name: string; ext: string }[] {
	let videoData = [];

	for (let base of videoPaths) {
		const name = parse(base).name;
		const ext = parse(base).ext;
		const path = base.split(name)[0];
		videoData.push({ base: base, path: path, name: name, ext: ext });
	}

	return videoData;
}

export function getVideoDuration(videoPath: string): Promise<number> {
	return new Promise<number>((resolve, reject) => {
		const cmd = FfmpegCommand();
		cmd.setFfmpegPath(getFFmpeg()[0]);
		cmd.setFfprobePath(getFFmpeg()[1]);
		cmd.input(videoPath);
		cmd.ffprobe((err, metadata) => {
			if (err) {
				reject(err);
			} else {
				const duration = metadata.format.duration as number;
				console.log(`Video duration: ${duration}`);
				resolve(duration);
			}
		});
	});
}

export function getCalculatedVideoBitrate(duration: number, targetFileSize: number): number {
	const magic = Math.max((targetFileSize * 8192.0) / (1.048576 * duration) - 128, 100);
	console.log(`Calculated bitrate: ${magic}`);
	return magic;
}

export function getFFmpeg(): [string, string] {
	let ffmpegPath: string = __dirname + "/ffmpeg.exe";
	let ffprobePath: string = __dirname + "/ffprobe.exe";

	if (process.platform === "linux") {
		const cmd = spawnSync("which", ["ffmpeg"], { encoding: "utf8" });

		if (cmd.stdout != "") {
			ffmpegPath = "ffmpeg";
			ffprobePath = "ffprobe";
		} else {
			require("./main").mainWindow.webContents.send("message", "FFmpeg missing!", "Please install FFmpeg before continuing");

			new Notification({ title: "FFmpeg missing!", body: "Please install FFmpeg before continuing" }).show();

			ffmpegPath = "null";
			ffprobePath = "null";
		}
	}

	return [ffmpegPath, ffprobePath];
}
