use std::env;
use std::process::{Command, ExitCode};
use std::fs;
use std::path::Path;
use std::collections::HashMap;
use std::process;
use inflector::Inflector;
use log::*;
use simplelog::{TermLogger, TerminalMode, ColorChoice,Config};
use serde::{Deserialize, Serialize};

// The settings this program takes from the .json file
// The .json file should be structured matching this struct
#[derive(Serialize, Deserialize, Debug)]
struct Settings {
    chapter: String,
    unity: String,
    system: String,
    checksum: Option<String>,
    path_id_overrides: Vec<(String, usize)>
}

// Force a particular file to use a Unity .assets PathID by renaming the file, typically in the 'output/assets' folder
fn force_path_id(directory_assets: &str, original_name: &str, path_id_override: usize) -> std::io::Result<()>
{
    let new_name = format!("{} {}", path_id_override, original_name);
    let original_path = format!("{}/{}", directory_assets, original_name);
    let new_path = format!("{}/{}", directory_assets, new_name);

    println!("Forcing path id {}: {} -> {}", path_id_override, original_path, new_path);
    fs::rename(original_path, new_path)
}

// Previously settings were read from cmd line, but now we load from .json
// When loading from .json, the first argument should be the path to the .json file.
fn read_settings_from_args_or_json() -> Settings
{
    let args: Vec<String> = env::args().collect();

    if args[1].ends_with(".json")
    {
        let json_path = args[1].to_string();
        println!("Loading settings from json file {}", json_path);
        let json_str = fs::read_to_string(json_path).expect("Unable to read json config file");
        serde_json::from_str(json_str.as_str()).expect("Unable to parse json file")
    }
    else
    {
        let chapter = args[1].to_string();
        let unity = args[2].to_string();
        let system = args[3].to_string();
        let checksum = if args.len() > 4 {
            Some(args[4].to_string())
        } else {
            None
        };

        Settings {
            chapter,
            unity,
            system,
            checksum,
            path_id_overrides: Vec::new()
        }
    }
}



fn main() -> ExitCode {
    TermLogger::init(
        LevelFilter::Trace,
        Config::default(),
        TerminalMode::Stdout,
        ColorChoice::Auto,
    )
    .expect("Failed to init logger");

    let settings = read_settings_from_args_or_json();
    let chapter = &settings.chapter;
    let unity = &settings.unity;
    let system = &settings.system;
    let checksum = settings.checksum.as_ref();
    println!("Rust Settings: {:?}", settings);

    // Check if python is correctly installed
    println!("Running 'python --version' to check if python is correctly installed...");
    let result = Command::new("python")
        .arg("--version")
        .status()
        .expect("Failed to run python");

    if !result.success()
    {
        println!("Python not found! via `python`. Make sure you:");
        println!("- ticked 'Add Python to environment variables' in the python installer.");
        println!("- can run 'python' in the console and get no error/the Microsoft Store does NOT appear");
        println!("Failed to run python: {:?}", result);
        return ExitCode::FAILURE;
    }

    let mut chapters = HashMap::new();
    chapters.insert("onikakushi", 1);
    chapters.insert("watanagashi", 2);
    chapters.insert("tatarigoroshi", 3);
    chapters.insert("himatsubushi", 4);
    chapters.insert("meakashi", 5);
    chapters.insert("tsumihoroboshi", 6);
    chapters.insert("minagoroshi", 7);
    chapters.insert("matsuribayashi", 8);
    chapters.insert("rei", 9);
    chapters.insert("hou-plus", 10);

    if !chapters.contains_key(&chapter[..]) {
        println!("Unknown chapter, should be one of {:?}", chapters.keys());
    }

    let arc_number = chapters.get(&chapter[..]).unwrap().clone();
    let assets_containing_folder = format!("assets/vanilla/{}/{}-{}{}", &chapter, &system, &unity, &format_checksum(checksum, "-"));
    let assets = format!("{}/{}", assets_containing_folder, "sharedassets0.assets");
    println!("Looking for vanilla assets at [{}]", assets);
    let directory_assets = "output/assets";

    // Example 'HigurashiEp05_Data' for Chapter 5
    let higu_ep_folder_name = format!("HigurashiEp{:02}_Data", arc_number);

    // Example 'output/HigurashiEp05_Data'
    let directory_data = format!("output/{}", higu_ep_folder_name);

    // Example 'output/HigurashiEp05_Data/meakashi_5.5.3p1_unix.emip'
    let emip = format!("{}/{}_{}_{}.emip", &directory_data, &chapter, &unity, &system);

    // Example 'Meakashi-UI_5.5.3p1_unix.7z'
    //to_title_case() replaces hyphens and underscores with spaces. If this happens, revert it by replacing spaces with hyphens.
    let archive = format!("{}-UI_{}_{}{}.7z", &chapter.to_title_case().replace(" ", "-"), &unity, &system, &format_checksum(checksum, "_"));

    if Path::new(&emip).exists() {
        fs::remove_file(&emip).expect("Failed to remove file");
    }
    if Path::new(&archive).exists() {
        fs::remove_file(&archive).expect("Failed to remove file");
    }
    if Path::new(&directory_assets).exists() {
        fs::remove_dir_all(&directory_assets).expect("Failed to remove directory");
    }
    fs::create_dir_all(&directory_assets).expect("Failed to recreate directory");
    if Path::new(&directory_data).exists() {
        fs::remove_dir_all(&directory_data).expect("Failed to remove directory");
    }
    fs::create_dir_all(&directory_data).expect("Failed to recreate directory");

    // 0. check version
    let output = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("scripts/AssetVersion.py")
        .arg(&assets)
        .output()
        .expect("failed to execute UnityTextModifier.py");

    assert!(output.status.success());

    let version = String::from_utf8_lossy(&output.stdout).into_owned();

    if unity != &version.trim() {
        println!("ERROR: Expected unity version {} but got version {}. If 'nothing found' then check the vanilla folder actually contains the required vanilla sharedassets!", unity,  &version.trim());
    }

    assert_eq!(unity, &version.trim());

    // 1. texts
    let status = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("scripts/UnityTextModifier.py")
        .arg(&assets)
        .arg("assets/text-edits.json")
        .arg(&directory_assets)
        .status()
        .expect("failed to execute UnityTextModifier.py");

    assert!(status.success());

    // 2. images
    copy_images("assets/images/shared", &directory_assets);
    if arc_number <= 4 {
        copy_images("assets/images/question_arcs", &directory_assets);
    } else if arc_number <= 8 {
        copy_images("assets/images/answer_arcs", &directory_assets);
    };
    copy_images(format!("assets/images/specific/{}", &chapter).as_ref(), &directory_assets);
    let version_specific_path = format!("assets/images/version-specific/{}-{}", &chapter, &unity);
    copy_images(version_specific_path.as_ref(), &directory_assets);
    if arc_number.clone() == 9 {
        fs::rename("output/assets/configbg_Texture2D.png", "output/assets/56configbg_Texture2D.png").expect("Unable to rename");
    } else if arc_number.clone() == 8 {
        fs::rename("output/assets/configbg_Texture2D.png", "output/assets/50configbg_Texture2D.png").expect("Unable to rename");
    } else {
        fs::rename("output/assets/configbg_Texture2D.png", "output/assets/47configbg_Texture2D.png").expect("Unable to rename");
    }
    let caretdir = match arc_number {
        1..=2 => "assets/files-5.2",
        3..=4 => "assets/files-5.3",
        5..=6 => "assets/files-5.5",
        7     => "assets/files-5.6",
        8     => "assets/files-2017.2",
        9     => "assets/files-rei",
        10    => "assets/files-hou-plus",
        _     => panic!("Couldn't determine folder for text carets with arc {}", arc_number)
    };
    copy_files(&caretdir, &directory_assets);
    println!();

    // 3. fonts - NOTE: Only applied for chapters 1-8. Fonts for Rei (Ch.9) and Hou Plus (Ch.10) will need to be generated manually
    // and saved in the files-rei and files-hou-plus folders.
    if arc_number.clone() < 9 {
        let mut font_path = format!("assets/vanilla/{}/{}-{}-fonts/msgothic_0.dat", &chapter, &system, &unity);
        if ! Path::new(&font_path).exists() {
            font_path = format!("assets/vanilla/{}/msgothic_0.dat", &chapter);
        }

        let unity_ver_str = match arc_number {
            1..=7 => "5",
            8     => "2017",
            9     => "2019",
            _     => panic!("Couldn't identify version for arc {}", arc_number),
        };

        let status = Command::new("python")
            .env("PYTHONIOENCODING", "utf-8")
            .arg("scripts/TMPAssetConverter.py")
            .arg("assets/fonts/msgothic_0 SDF Atlas_Texture2D.dat")
            .arg("assets/fonts/msgothic_0 SDF_TextMeshProFont.dat")
            .arg(font_path)
            .arg(&directory_assets)
            .arg(&unity_ver_str)
            .status()
            .expect("failed to execute TMPAssetConverter.py");

        assert!(status.success());

        let mut font_path = format!("assets/vanilla/{}/{}-{}-fonts/msgothic_2.dat", &chapter, &system, &unity);
        if ! Path::new(&font_path).exists() {
            font_path = format!("assets/vanilla/{}/msgothic_2.dat", &chapter);
        }

        let status = Command::new("python")
            .env("PYTHONIOENCODING", "utf-8")
            .arg("scripts/TMPAssetConverter.py")
            .arg("assets/fonts/msgothic_2 SDF Atlas_Texture2D.dat")
            .arg("assets/fonts/msgothic_2 SDF_TextMeshProFont.dat")
            .arg(font_path)
            .arg(&directory_assets)
            .arg(&unity_ver_str)
            .status()
            .expect("failed to execute TMPAssetConverter.py");

        assert!(status.success());

        println!();
    }

    // 4. copy assets
    copy_files(assets_containing_folder.as_ref(), &directory_data);

    println!();

    // 4a. Force certain assets to have specific PathIDs
    if settings.path_id_overrides.len() > 0 {
        println!("------ Forcing PathIDs ------");
    }
    for (original_name, path_id_override) in settings.path_id_overrides {
        force_path_id(&directory_assets, &original_name, path_id_override).expect("Failed to force ID");
    }

    // 5. generate emip
    let status = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("scripts/EMIPGenerator.py")
        .arg(format!("{}/sharedassets0.assets", &directory_data))
        .arg(&directory_assets)
        .arg(&emip)
        .status()
        .expect("failed to execute EMIPGenerator.py");

    assert!(status.success());

    println!();

    // 6. apply emip
    let status = Command::new("AssetBundleExtractor")
        .arg("applyemip")
        .arg(&emip)
        .arg("output")
        .status()
        .expect("failed to execute AssetBundleExtractor");

    println!("AssetBundleExtractor Status: {}", status);

    assert!(status.success());

    // 7. pack with 7zip
    // Note: We run 7zip from inside the "output" folder so the final archive just contains
    // 'HigurashiEp05_Data/sharedassets0.assets' (otherwise it would be 'output/HigurashiEp05_Data/sharedassets0.assets')
    let cwd = "output".to_string();
    let files_to_archive = format!("{}/sharedassets0.assets", higu_ep_folder_name);

    let result_7za = pack_7zip("7za", &archive, &cwd, &files_to_archive);

    let status: std::io::Result<process::ExitStatus> = match result_7za {
        Ok(ok) => Ok(ok),
        Err(err) => match err.kind() {
            std::io::ErrorKind::NotFound => {
                println!("Warning: '7za' not found - trying '7z' instead");
                pack_7zip("7z", &archive, &cwd, &files_to_archive)
            },
            _ => Err(err),
        }
    };

    let exit_status = status.expect("failed to execute 7za or 7z");

    assert!(exit_status.success());

    return ExitCode::SUCCESS;
}

fn format_checksum(checksum: Option<&String>, sep: &str) -> String
{
    return checksum.map_or("".to_string(), |c| format!("{}{}", sep, c));
}

fn pack_7zip(command: &str, archive: &String, cwd: &String, path: &String) -> std::io::Result<process::ExitStatus> {
    println!("[7-Zip] Running {} in working directory: [{}] and path: [{}]...", command, cwd, path);

    Command::new(command)
    .current_dir(cwd)
    .arg("a")
    .arg("-t7z")
    .arg(archive)
    .arg(path)
    .status()
}

fn copy_images(from: &str, to: &str) {
    if ! Path::new(&from).exists() {
        println!("Path {} not found", from);
        return
    }
    println!("Copying images from {}", from);
    for entry in fs::read_dir(from).expect("Can't read directory") {
        let path = entry.unwrap().path();
        let to_path = format!("{}/{}_Texture2D.png", to, path.file_stem().unwrap().to_str().unwrap());
        println!("Copying Image {} -> {}", path.to_string_lossy(), to_path);
        fs::copy(&path, to_path).expect("Unable to copy");
    }
}

fn copy_files(from: &str, to: &str) {
    if ! Path::new(&from).exists() {
        println!("Path {} not found", from);
        return
    }
    println!("Copying files from {}", from);
    for entry in fs::read_dir(from).expect("Can't read directory") {
        let path = entry.unwrap().path();

        // Ignore paths starting with '.ignore' and emit warning
        if let Some(name) = path.file_name() {
            let name = name.to_os_string();
            if name.to_string_lossy().to_lowercase().starts_with(".ignore")
            {
                warn!("Skipping path {:?} as it starts with '.ignore'", path);
                continue;
            }
        }

        // For now, subdirectories are not supported
        if path.is_dir()
        {
            error!("Found subdirectory at {:?} - Subdirectories not supported, please remove or prepend with 'IGNORE' to ignore.", path);
            panic!("Exiting due to unexpected subdirectory");
        }

        let to_path = format!("{}/{}", to, path.file_name().unwrap().to_str().unwrap());
        println!("Copying File {} -> {}", path.to_string_lossy(), to_path);
        fs::copy(&path, to_path).expect("Unable to copy");
    }
}
