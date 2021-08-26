use std::env::current_dir;
use std::fs::read_dir;
use std::process::Command;

#[allow(dead_code)]
pub fn get_current_directory() -> String {
    let path = current_dir()
        .expect("Couldn't get current directory!");

    return format!("{}", path.display());
}

#[allow(dead_code)]
pub fn get_files_in_current_directory() -> Vec<String> {
    let mut files = vec![];
    let paths = read_dir(".").unwrap();

    for p in paths {
        let file = p.unwrap()
            .path()
            .display()
            .to_string()
            .replace("./", "");
        
        files.push(file);
    }
    
    return files;
}

#[allow(dead_code)]
pub fn get_files_of_type_in_current_directory(file_type: &str) -> Vec<String> {
    let all_files = get_files_in_current_directory();
    let mut files = vec![];

    for f in all_files {
        if f.contains(file_type) {
            files.push(f);
        }
    }

    return files;
}

#[allow(dead_code)]
pub fn get_video_duration(video_path: &str) -> f32 {
    let result: f32 = run_command("ffprobe",
        vec![
            "-v", 
            "error", 
            "-show_entries", 
            "format=duration", 
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
    ).trim().parse().unwrap_or(0.0);

    println!("Video duration: {}", result);
    return result;
}

#[allow(dead_code)]
pub fn calculate_video_bitrate(video_path: &str, audio_bitrate: f32, target_file_size: f32) -> f32 {
    let duration: f32 = get_video_duration(video_path);
    let calc = (target_file_size * 8192.0) / (1.048576 * duration) - (audio_bitrate + 8.0);
    let new_bitrate = calc.max(1.0);

    println!("Calculated bitrate: {}", new_bitrate);
    return new_bitrate;
}

pub fn run_command(cmd: &str, args: Vec<&str>) -> String {
    let output = Command::new(cmd)
        .args(args)
        .output()
        .expect("Failed!");
    
    println!("status: {}", output.status);
    println!("stdout: {}", String::from_utf8_lossy(&output.stdout));
    println!("stderr: {}", String::from_utf8_lossy(&output.stderr));

    // assert!(output.status.success());
    
    return String::from_utf8_lossy(&output.stdout).to_string();
}