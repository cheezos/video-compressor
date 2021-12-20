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
	return new Promise<boolean>((resolve) => {
		let currentVideo: number = 0;

		const compress = () => {
			console.log(`Compressing ${currentVideo + 1}/${videoData.length}...`);

			const cmd = FfmpegCommand();
			cmd.setFfmpegPath(__dirname + "/ffmpeg.exe");
			cmd.setFfprobePath(__dirname + "/ffprobe.exe");
			cmd.input(videoData[currentVideo].base);
			cmd.videoCodec("libx264");
			cmd.fps(30);
			cmd.output(`${videoData[currentVideo].path}/${videoData[currentVideo].name}-compressed.${videoData[currentVideo].ext}`);
			cmd.on("end", () => {
				console.log(`Compressed ${currentVideo + 1}/${videoData.length}`);

				if (currentVideo + 1 < videoData.length) {
					currentVideo += 1;
					compress();
				} else {
					resolve(true);
				}
			});
			cmd.run();
		};

		compress();
	});
}
