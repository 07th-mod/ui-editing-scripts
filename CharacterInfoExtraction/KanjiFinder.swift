import Foundation

var standardError = FileHandle.standardError

extension FileHandle : TextOutputStream {
	public func write(_ string: String) {
		guard let data = string.data(using: .utf8) else { return }
		self.write(data)
	}
}

guard CommandLine.arguments.count > 1 else {
	print("""
		Usage: \(CommandLine.arguments[0]) [-filter filterFile.txt] assetBundle1.assets [assetBundle2.assets ...]
		Use - to read from stdin
		Finds 3-byte unicode characters (like kanji) in files
		If a filter is supplied, only characters also in the filter will be outputted
		""", to: &standardError)
	exit(EXIT_FAILURE)
}

#if !swift(>=4.2)
extension Collection {
	func firstIndex(where predicate: (Element) throws -> Bool) rethrows -> Index? {
		return try self.index(where: predicate)
	}
}
#endif

var filter: String? = nil
var inFiles: [String] = Array(CommandLine.arguments[1...])

if let filterIndex = inFiles.firstIndex(where: { $0.lowercased() == "-filter" }) {
	if filterIndex + 1 < inFiles.endIndex {
		filter = try String(contentsOf: URL(fileURLWithPath: inFiles[filterIndex + 1]))
		inFiles[filterIndex...filterIndex+1] = []
	}
}

let bundles: [Data]
if inFiles == ["-"] {
	bundles = [FileHandle.standardInput.readDataToEndOfFile()]
} else {
	bundles = try inFiles.map { try Data(contentsOf: URL(fileURLWithPath: $0)) }
}

extension UTF8.CodeUnit {
	var isStart3: Bool {
		return self & 0b11110000 == 0b11100000
	}
	var isContinuation: Bool {
		return self & 0b11000000 == 0b10000000
	}
}

func unicodeFinder(data: [UInt8], minLength: Int = 2) -> String {
	var out = [UInt8]()
	var left = data[...]
	while true {
		guard let index = left.firstIndex(where: { ($0 & 0b11110000) == 0b11100000 }) else { break }
		left = left[index...]
		guard left.count > 5 else { break }
		var good = 0
		for i in stride(from: left.startIndex, to: left.endIndex, by: 3) {
			if left[i].isStart3 && left[i+1].isContinuation && left[i+2].isContinuation {
				good += 1
			}
			else {
				if good >= minLength {
					out.append(contentsOf: left[..<i])
					good = 0
				}
				left = left[(i+1)...]
				break
			}
		}
		if good >= minLength {
			out.append(contentsOf: left.prefix(left.count / 3 * 3))
		}
	}
	return String(decoding: out, as: UTF8.self)
}

let unicodeStrings = bundles.map({ unicodeFinder(data: Array($0)) })
var chars = unicodeStrings.map({ Set($0.unicodeScalars) }).reduce(Set(), { $0.union($1) })
if let filter = filter {
	chars.formIntersection(filter.unicodeScalars)
}

print(String(chars.sorted().lazy.map(Character.init)), terminator: "")
