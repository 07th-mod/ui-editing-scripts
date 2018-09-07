use std::env;
use std::collections::HashMap;
use std::process::Command;
use std::fs;
use std::path::Path;

fn main() {
    let args: Vec<String> = env::args().collect();
    let platform = &args[2];

    let mut chapters = HashMap::new();

    chapters.insert("oni".to_string(), "onikakushi");
    chapters.insert("wata".to_string(), "watanagashi");
    chapters.insert("tata".to_string(), "tatarigoroshi-steam");
    chapters.insert("tata-mg".to_string(), "tatarigoroshi-mg");
    chapters.insert("hima".to_string(), "himatsubushi");
    chapters.insert("mea".to_string(), "meakashi");
    chapters.insert("tsumi".to_string(), "tsumihoroboshi");

    let chapter = chapters.get(&args[1]).expect("Unknown chapter");
    let assets = format!("assets/vanilla/{}/{}/sharedassets0.assets", chapter, platform);
    let directory = "output/assets";

    if Path::new(&directory).exists() {
        fs::remove_dir_all(&directory).expect("Failed to remove directory");
    }
    fs::create_dir_all(&directory).expect("Failed to recreate directory");

    let output = Command::new("python")
        .env("PYTHONIOENCODING", "utf-8")
        .arg("../ui-editing-scripts/UnityTextModifier.py")
        .arg(format!("{}", assets))
        .arg(format!("assets/text-edits.json"))
        .arg(format!("{}", directory))
        .output()
        .expect("failed to execute UnityTextModifier.py");

    if output.status.success() {
        println!("{}", String::from_utf8_lossy(&output.stdout));
    } else {
        println!("{}", String::from_utf8_lossy(&output.stderr));
    }
}
