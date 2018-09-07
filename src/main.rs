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

    if Path::new(&directory).exists() {
        fs::remove_dir_all("output/assets").expect("Failed to remove directory");
    }
    fs::create_dir_all("output/assets").expect("Failed to recreate directory");

    // 1. texts
    let output = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("../ui-editing-scripts/UnityTextModifier.py")
        .arg(format!("{}", &assets))
        .arg(format!("assets/text-edits.json"))
        .arg(format!("{}", &directory))
        .output()
        .expect("failed to execute UnityTextModifier.py");

    if output.status.success() {
        println!("{}", String::from_utf8_lossy(&output.stdout));
    } else {
        println!("{}", String::from_utf8_lossy(&output.stderr));
    }

    // 2. images
    copy_files("assets/images/shared", directory);
    copy_files(format!("assets/images/{}", &arc_type).as_ref(), directory);
    copy_files(format!("assets/images/specific/{}", &chapter).as_ref(), directory);
    fs::rename("output/assets/configbg_Texture2D.png", "output/assets/47configbg_Texture2D.png").expect("Unable to rename");

    // 3. fonts
}

fn copy_files(from: &str, to: &str) {
    println!("Copying files from {}", from);
    for entry in fs::read_dir(from).expect("Can't read directory") {
        let path = entry.unwrap().path();
        fs::copy(&path, format!("{}/{}_Texture2D.png", to, path.file_stem().unwrap().to_str().unwrap())).expect("Unable to copy");
    }
}