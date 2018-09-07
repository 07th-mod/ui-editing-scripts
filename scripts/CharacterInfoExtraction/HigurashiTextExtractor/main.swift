import Foundation

guard CommandLine.arguments.count > 1 else {
	print("Usage: \(CommandLine.arguments[0]) file [(e|j)]\nExtracts text from Higurashi script files.  Use e or j to specify English or Japanese, otherwise you'll get both")
	exit(EXIT_FAILURE)
}

var verbose = false
var mode = 3
if CommandLine.arguments.count >= 3 {
	if CommandLine.arguments.contains(where: { $0.lowercased() == "e" }) { mode = 2 }
	if CommandLine.arguments.contains(where: { $0.lowercased() == "j" }) { mode = 1 }
	if CommandLine.arguments.contains(where: { $0.lowercased() == "-v" }) { verbose = true }
}

var standardError = FileHandle.standardError

extension FileHandle : TextOutputStream {
	public func write(_ string: String) {
		guard let data = string.data(using: .utf8) else { return }
		self.write(data)
	}
}

struct Command {
	let name: String
	let arguments: [Token]
	
	init?(tokens: [Token]) {
		guard tokens.count >= 3 else { return nil }
		guard tokens[0].type == .identifier else { return nil }
		guard tokens[1].type == .punctuation && tokens[1].value == "(" else { return nil }
		guard tokens.last!.type == .punctuation && tokens.last!.value == ")" else { return nil }
		self.name = tokens[0].value
		self.arguments = tokens.dropFirst(2).dropLast().filter({ $0.value != "," })
	}
}

func loadFile(path: String) throws -> [[Token]] {
	let file: String
	if path == "-" {
		file = String(decoding: FileHandle.standardInput.readDataToEndOfFile(), as: UTF8.self)
	} else {
		file = try String(contentsOf: URL(fileURLWithPath: path))
	}
	let tokens = try Token.tokenize(input: file)
	let statements = tokens.split(whereSeparator: { $0.value == ";" || $0.value == "{" || $0.value == "}" }).map(Array.init)
	return statements
}



let tokens = try loadFile(path: CommandLine.arguments[1])
let commands = tokens.compactMap { tokens -> Command? in
	let output = Command(tokens: tokens)
	if (output == nil) {
		if verbose { print("\(tokens) was not a command!", to: &standardError) }
	}
	return output
}

let ignore: Set = ["FadeOutBGM", "DisableWindow", "DrawScene", "PlayBGM", "Wait", "SetValidityOfInput", "DrawSceneWithMask", "SetSpeedOfMessage", "DrawBustshot", "FadeBustshot", "DrawBustshotWithFiltering", "FadeBustshotWithFiltering", "PlaySE", "ShakeScreen", "DrawFilm", "FadeFilm", "FadeAllBustshots", "DrawSpriteWithFiltering", "MoveSprite", "DrawSprite", "FadeSprite", "TitleScreen", "SetLocalFlag", "ShowChapterPreview", "SetCharSpacing", "SetLineSpacing", "SetScreenAspect", "SetWindowPos", "SetWindowSize", "SetWindowMargins", "FadeBG", "SetValidityOfSkipping", "SetGUIPosition", "SetStyleOfMessageSwinging", "EnableJumpingOfReturnIcon", "SetValidityOfTextFade", "SetValidityOfInterface", "Negative", "CallScript", "SavePoint", "SetValidityOfWindowDisablingWhenGraphicsControl", "SetFontSize", "SetNameFormat", "SetFontId", "StopBGM", "SetGlobalFlag", "LanguagePrompt", "SetValidityOfSaving", "ShowTips", "CheckTipsAchievements", "if", "StoreValueToLocalWork", "DrawBG", "ChangeScene", "StopSE", "ShakeScreenSx", "StopSE", "GetAchievement", "CallSection", "JumpSection", "SetDrawingPointOfMessage"]
var japanese = ""
var english = ""

func stringFromLiteral(literal: Token) -> String {
	guard literal.type == .stringLiteral else { 
		if literal.value == "NULL" { return "" }
		fatalError("\(literal) wasn't a string literal!") 
	}
	return literal.value.replacingOccurrences(of: "\\\"", with: "\"").replacingOccurrences(of: "\\n", with: "\n")
}

for command in commands {
	if ignore.contains(command.name) { continue }
	
	switch command.name {
	case "OutputLine":
		japanese += stringFromLiteral(literal: command.arguments[1])
		english += stringFromLiteral(literal: command.arguments[3])
	case "OutputLineAll":
		let line = stringFromLiteral(literal: command.arguments[1])
		japanese += line
		english += line
	case "ClearMessage":
		japanese += "\n\n"
		english += "\n\n"
	default: if verbose { print(command, to: &standardError) }
	}
}

if mode & 1 > 0 { print(japanese) }
if mode & 2 > 0 { print(english) }
