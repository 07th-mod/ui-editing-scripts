import Foundation

var standardError = FileHandle.standardError

extension FileHandle : TextOutputStream {
	public func write(_ string: String) {
		guard let data = string.data(using: .utf8) else { return }
		self.write(data)
	}
}

guard CommandLine.arguments.count > 1 else {
	print("Usage: \(CommandLine.arguments[0]) file\nUse - to read from stdin", to: &standardError)
	exit(EXIT_FAILURE)
}
let input: String
if CommandLine.arguments[1] == "-" {
	input = String(decoding: FileHandle.standardInput.readDataToEndOfFile(), as: UTF8.self)
} else {
	input = try String(contentsOf: URL(fileURLWithPath: CommandLine.arguments[1]))
}
let chars = Set(input.unicodeScalars)
let out = chars.sorted().lazy.map(Character.init)
print(String(out), terminator: "")
