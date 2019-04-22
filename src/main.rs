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
    let platform = &args[2];
    let system = &args[3];

    let mut chapters = HashMap::new();
    chapters.insert("onikakushi".to_string(), 1);
    chapters.insert("watanagashi".to_string(), 2);
    chapters.insert("tatarigoroshi".to_string(), 3);
    chapters.insert("himatsubushi".to_string(), 4);
    chapters.insert("meakashi".to_string(), 5);
    chapters.insert("tsumihoroboshi".to_string(), 6);

    if !chapters.contains_key(chapter) {
        println!("Unknown chapter");
        process::exit(1);
    }

    let arc_number = chapters.get(chapter).unwrap();
    let arc_type = if arc_number <= &4 { "question_arcs" } else { "answer_arcs" };
    let assets = format!("assets/vanilla/{}/{}/{}/sharedassets0.assets", chapter, platform, system);
    let directory_assets = "output/assets";
    let directory_data = format!("output/HigurashiEp{:02}_Data", arc_number);
    let emip = format!("{}/{}_{}_{}.emip", &directory_data, &chapter, &platform, &system);
    let archive = format!("{}-UI_{}_{}.7z", &chapter.to_title_case(), &platform, &system);

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
    fs::rename("output/assets/configbg_Texture2D.png", "output/assets/47configbg_Texture2D.png").expect("Unable to rename");
    println!();

    // 3. fonts
    let status = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("scripts/TMPAssetConverter.py")
        .arg("assets/fonts/msgothic_0_SDF_Atlas_Texture2D.dat")
        .arg("assets/fonts/msgothic_0_SDF_TextMeshProFont.dat")
        .arg(format!("assets/vanilla/{}/{}/msgothic_0.dat", &chapter, platform))
        .arg(&directory_assets)
        .status()
        .expect("failed to execute TMPAssetConverter.py");

    assert!(status.success());

    let status = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("scripts/TMPAssetConverter.py")
        .arg("assets/fonts/msgothic_2_SDF_Atlas_Texture2D.dat")
        .arg("assets/fonts/msgothic_2_SDF_TextMeshProFont.dat")
        .arg(format!("assets/vanilla/{}/{}/msgothic_2.dat", &chapter, platform))
        .arg(&directory_assets)
        .status()
        .expect("failed to execute TMPAssetConverter.py");

    assert!(status.success());

    println!();

    // 4. copy assets
    copy_files(format!("assets/vanilla/{}/{}/{}", chapter, platform, system).as_ref(), &directory_data);

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
    fs::remove_file(&emip).expect("Failed to remove file");

    // 7. pack with 7xip
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
