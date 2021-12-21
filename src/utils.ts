import { parse } from "path";
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
		cmd.setFfmpegPath(__dirname + "/ffmpeg.exe");
		cmd.setFfprobePath(__dirname + "/ffprobe.exe");
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
	let magic = Math.max((targetFileSize * 8192.0) / (1.048576 * duration) - 128, 100);
	console.log(`Calculated bitrate: ${magic}`);
	return magic;
}
