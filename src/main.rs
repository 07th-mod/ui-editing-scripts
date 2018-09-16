use std::env;
use std::process::Command;
use std::fs;
use std::path::Path;

fn main() {
    let args: Vec<String> = env::args().collect();
    let chapter = &args[1];
    let platform = &args[2];

    let arc_type = if chapter == "onikakushi" || chapter == "watanagashi" || chapter == "tatarigoroshi" || chapter == "himatsubushi" { "question_arcs" } else { "answer_arcs" };
    let assets = format!("assets/vanilla/{}/{}/sharedassets0.assets", chapter, platform);
    let directory = "output/assets";
    let emip = format!("output/{}-{}.emip", &chapter, &platform);

    if Path::new(&emip).exists() {
        fs::remove_file(&emip).expect("Failed to remove file");
    }
    if Path::new(&directory).exists() {
        fs::remove_dir_all("output/assets").expect("Failed to remove directory");
    }
    fs::create_dir_all("output/assets").expect("Failed to recreate directory");

    // 1. texts
    let output = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("scripts/UnityTextModifier.py")
        .arg(&assets)
        .arg("assets/text-edits.json")
        .arg(&directory)
        .output()
        .expect("failed to execute UnityTextModifier.py");

    if output.status.success() {
        println!("{}", String::from_utf8_lossy(&output.stdout));
    } else {
        println!("{}", String::from_utf8_lossy(&output.stderr));
    }

    // 2. images
    copy_files("assets/images/shared", &directory);
    copy_files(format!("assets/images/{}", &arc_type).as_ref(), &directory);
    copy_files(format!("assets/images/specific/{}", &chapter).as_ref(), &directory);
    fs::rename("output/assets/configbg_Texture2D.png", "output/assets/47configbg_Texture2D.png").expect("Unable to rename");
    println!();

    // 3. fonts
    let output = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("scripts/TMPAssetConverter.py")
        .arg("assets/fonts/msgothic_0 SDF Atlas_Texture2D.dat")
        .arg("assets/fonts/msgothic_0 SDF_TextMeshProFont.dat")
        .arg(format!("assets/vanilla/{}/msgothic_0.dat", &chapter))
        .arg(&directory)
        .output()
        .expect("failed to execute TMPAssetConverter.py");

    if output.status.success() {
        println!("{}", String::from_utf8_lossy(&output.stdout));
    } else {
        println!("{}", String::from_utf8_lossy(&output.stderr));
    }

    let output = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("scripts/TMPAssetConverter.py")
        .arg("assets/fonts/msgothic_2 SDF Atlas_Texture2D.dat")
        .arg("assets/fonts/msgothic_2 SDF_TextMeshProFont.dat")
        .arg(format!("assets/vanilla/{}/msgothic_2.dat", &chapter))
        .arg(&directory)
        .output()
        .expect("failed to execute TMPAssetConverter.py");

    if output.status.success() {
        println!("{}", String::from_utf8_lossy(&output.stdout));
    } else {
        println!("{}", String::from_utf8_lossy(&output.stderr));
    }

    println!();

    // 4. emip
    let output = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("scripts/EMIPGenerator.py")
        .arg(&assets)
        .arg(&directory)
        .arg(&emip)
        .output()
        .expect("failed to execute EMIPGenerator.py");

    if output.status.success() {
        println!("{}", String::from_utf8_lossy(&output.stdout));
    } else {
        println!("{}", String::from_utf8_lossy(&output.stderr));
    }
}

fn copy_files(from: &str, to: &str) {
    println!("Copying files from {}", from);
    for entry in fs::read_dir(from).expect("Can't read directory") {
        let path = entry.unwrap().path();
        fs::copy(&path, format!("{}/{}_Texture2D.png", to, path.file_stem().unwrap().to_str().unwrap())).expect("Unable to copy");
    }
}
