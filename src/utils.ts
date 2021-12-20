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

export function compressQueue(videoData: { base: string; path: string; name: string; ext: string }[]): Promise<boolean> {
	return new Promise<boolean>((resolve, reject) => {
		let currentVideo: number = 0;

		const compress = () => {
			console.log(`Compressing ${currentVideo + 1}/${videoData.length}...`);

			getVideoDuration(videoData[currentVideo].base)
				.then((duration: number) => {
					const bitrate = getCalculatedVideoBitrate(duration);

					compressVideo(videoData[currentVideo], bitrate)
						.then(() => {
							if (currentVideo + 1 < videoData.length) {
								currentVideo += 1;
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

function compressVideo(videoData: { base: string; path: string; name: string; ext: string }, bitrate: number): Promise<boolean> {
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
			const cmd = FfmpegCommand();
			cmd.setFfmpegPath(__dirname + "/ffmpeg.exe");
			cmd.setFfprobePath(__dirname + "/ffprobe.exe");

			cmd.input(input);
			cmd.outputOptions(pass2);
			cmd.output(`${videoData.path}${videoData.name}-compressed${videoData.ext}`);

			cmd.on("end", () => {
				console.log(`Compressed ${videoData.name}`);
				resolve(true);
			});

			cmd.on("error", (err) => {
				reject(err);
			});

			cmd.run();
			console.log("Pass 2...");
		});

		cmd.on("error", (err) => {
			reject(err);
		});

		cmd.run();
		console.log("Pass 1...");
	});
}

function getVideoDuration(videoPath: string): Promise<number> {
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

function getCalculatedVideoBitrate(duration: number): number {
	let magic = Math.max((8.0 * 8192.0) / (1.048576 * duration) - 128, 100);
	console.log(`Calculated bitrate: ${magic}`);
	return magic;
}

// function clamp(value: number, min: number, max: number): number {
// 	return Math.min(Math.max(value, min), max);
// }
