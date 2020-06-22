extern crate inflector;

use std::env;
use std::process::Command;
use std::fs;
use std::path::Path;
use std::collections::HashMap;
use std::process;
use inflector::Inflector;

fn main() {
    let args: Vec<String> = env::args().collect();
    let chapter = &args[1];
    let unity = &args[2];
    let system = &args[3];

    let mut chapters = HashMap::new();
    chapters.insert("onikakushi", 1);
    chapters.insert("watanagashi", 2);
    chapters.insert("tatarigoroshi", 3);
    chapters.insert("himatsubushi", 4);
    chapters.insert("meakashi", 5);
    chapters.insert("tsumihoroboshi", 6);
    chapters.insert("minagoroshi", 7);
    chapters.insert("matsuribayashi", 8);

    if !chapters.contains_key(&chapter[..]) {
        println!("Unknown chapter");
        process::exit(1);
    }

    let arc_number = chapters.get(&chapter[..]).unwrap();
    let arc_type = if arc_number <= &4 { "question_arcs" } else { "answer_arcs" };
    let assets = format!("assets/vanilla/{}/{}-{}/sharedassets0.assets", &chapter, &system, &unity);
    let directory_assets = "output/assets";
    let directory_data = format!("output/HigurashiEp{:02}_Data", &arc_number);
    let emip = format!("{}/{}_{}_{}.emip", &directory_data, &chapter, &unity, &system);
    let archive = format!("{}-UI_{}_{}.7z", &chapter.to_title_case(), &unity, &system);

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

    let version = String::from_utf8_lossy(&output.stdout).into_owned();

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
    copy_images(format!("assets/images/{}", &arc_type).as_ref(), &directory_assets);
    copy_images(format!("assets/images/specific/{}", &chapter).as_ref(), &directory_assets);
    let version_specific_path = format!("assets/images/version-specific/{}-{}", &chapter, &unity);
    if Path::new(&version_specific_path).exists() {
        copy_images(version_specific_path.as_ref(), &directory_assets);
    }
    if arc_number.clone() == 8 {
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
        _     => panic!("Couldn't folder for text carets with arc {}", arc_number)
    };
    copy_files(&caretdir, &directory_assets);
    println!();

    // 3. fonts
    let mut font_path = format!("assets/vanilla/{}/{}-{}-fonts/msgothic_0.dat", &chapter, &system, &unity);
    if ! Path::new(&font_path).exists() {
        font_path = format!("assets/vanilla/{}/msgothic_0.dat", &chapter);
    }

    let unity_ver_str = if *arc_number >= 8 { "2017" } else { "5" };

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

    // 4. copy assets
    copy_files(format!("assets/vanilla/{}/{}-{}", &chapter, &system, &unity).as_ref(), &directory_data);

    println!();

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

    assert!(status.success());

    fs::remove_file(format!("{}/sharedassets0.assets.bak0000", &directory_data)).expect("Failed to remove file");
    let res_file = format!("{}/sharedassets0.assets.resS", &directory_data);
    if Path::new(&res_file).exists() {
        fs::remove_file(&res_file).expect("Failed to remove file");
    }
    fs::remove_file(&emip).expect("Failed to remove file");

    // 7. pack with 7zip
    let status = Command::new("7za")
        .current_dir("output")
        .arg("a")
        .arg("-t7z")
        .arg(&archive)
        .arg(format!("../{}", &directory_data))
        .status()
        .expect("failed to execute 7ze");

    assert!(status.success());
}

fn copy_images(from: &str, to: &str) {
    println!("Copying files from {}", from);
    for entry in fs::read_dir(from).expect("Can't read directory") {
        let path = entry.unwrap().path();
        fs::copy(&path, format!("{}/{}_Texture2D.png", to, path.file_stem().unwrap().to_str().unwrap())).expect("Unable to copy");
    }
}

fn copy_files(from: &str, to: &str) {
    println!("Copying files from {}", from);
    for entry in fs::read_dir(from).expect("Can't read directory") {
        let path = entry.unwrap().path();
        fs::copy(&path, format!("{}/{}", to, path.file_name().unwrap().to_str().unwrap())).expect("Unable to copy");
    }
}
