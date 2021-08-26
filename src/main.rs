use std::io::{stdin, self, Write};
mod utils;

fn main() {
    let mut entry_1 = String::new();
    print!("Enter the relative path to a video: ");

    io::stdout().flush().unwrap();
    stdin().read_line(&mut entry_1)
        .expect("Incorrect string.");
    
    let input = entry_1.trim(); // Replace with a function to validate the path
    let mut entry_2 = String::new();
    print!("Enter a target file size for your video: ");

    io::stdout().flush().unwrap();
    stdin().read_line(&mut entry_2)
        .expect("Incorrect string.");
    
    let target_file_size: f32 = entry_2.trim().parse().unwrap_or(1.0);
    let output = "out.mp4";
    let audio_bitrate = 64.0;
    let audio_bitrate_str = format!("{}k", audio_bitrate.to_string());
    let bitrate = format!("{}k", utils::calculate_video_bitrate(input, audio_bitrate, target_file_size).to_string());
    let bitrate_str = bitrate.as_str();

    println!("Compressing...");

    utils::run_command("ffmpeg",
        vec![
            "-y",
            "-i",
            input,
            "-c:v",
            "libx264",
            "-b:v",
            bitrate_str,
            "-c:a",
            "aac",
            "-b:a",
            audio_bitrate_str.as_str(),
            output
        ]
    );

    println!("Done! Look for your video titled 'out.mp4' in this directory.");
}