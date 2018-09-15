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
		Usage: \(CommandLine.arguments[0]) assetBundle1.assets [assetBundle2.assets ...]
		Use - to read from stdin
		Finds strings in Unity asset bundles
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

let inFiles: [String] = Array(CommandLine.arguments[1...])

extension Collection {
	subscript(offset offset: Int) -> Element {
		get {
			let i = index(startIndex, offsetBy: offset)
			return self[i]
		}
	}
}

func isUTF8Continuation(_ byte: UInt8) -> Bool {
	return byte & 0b1100_0000 == 0b1000_0000
}

func isValidUTF8<C: Collection>(data: C) -> Bool where C.Element == UInt8 {
	var slice = data[...]
	while !slice.isEmpty {
		let byte = slice.first!
		slice = slice.dropFirst()
		if byte & 0b1000_0000 == 0 { // Single byte utf-8
			// Strings shouldn't contain ASCII controll chars
			guard byte > 8 else { return false }
			guard !(0xe...0x1f).contains(byte) else { return false }
			continue
		}
		else if byte & 0b1110_0000 == 0b1100_0000 { // Two byte utf-8
			guard let cont = slice.first else { return false }
			guard isUTF8Continuation(cont) else { return false }
			slice = slice.dropFirst()
		}
		else if byte & 0b1111_0000 == 0b1110_0000 { // Three byte utf-8
			guard slice.count > 1 else { return false }
			guard isUTF8Continuation(slice[offset: 0]) else { return false }
			guard isUTF8Continuation(slice[offset: 1]) else { return false }
			slice = slice.dropFirst(2)
		}
		else if byte & 0b1111_1000 == 0b1111_0000 { // Four byte utf-8
			guard slice.count > 2 else { return false }
			guard isUTF8Continuation(slice[offset: 0]) else { return false }
			guard isUTF8Continuation(slice[offset: 1]) else { return false }
			guard isUTF8Continuation(slice[offset: 2]) else { return false }
			slice = slice.dropFirst(3)
		}
		else {
			return false
		}
	}
	return true
}

func stringFinder(data: Data, maxStringLength: Int = 100) -> [String] {
	return data.withUnsafeBytes { (ptr: UnsafePointer<UInt8>) -> [String] in
		let buffer = UnsafeRawBufferPointer(start: UnsafeRawPointer(ptr), count: data.count)
		guard data.count % 4 == 0 else { fatalError("Input file wasn't 4-byte aligned, it's probably not an asset bundle") }
		var out: [String] = []
		let ints = buffer.bindMemory(to: UInt32.self)
		for (index, int) in ints.lazy.map({ $0.littleEndian }).enumerated() {
			guard int > 1 && int < maxStringLength && int < ((ints.count - index - 1) * 4) else {
				continue
			}
			let uint32Length = Int((int &+ 3) / 4)
			let padding = ((4 - (int % 4)) % 4)
			let unicode = UnsafeBufferPointer(rebasing: ints[(index + 1)...].prefix(uint32Length))
			// Ensure padding is all 0s
			guard padding == 0 || unicode.last!.littleEndian &>> (padding * 8) == 0 else { continue }
			let optionalStr = unicode.withMemoryRebound(to: UInt8.self) { (unicode) -> String? in
				let stringUnicode = unicode[..<Int(int)]
				guard isValidUTF8(data: stringUnicode) else { return nil }
				return String(decoding: stringUnicode, as: UTF8.self)
			}
			guard let str = optionalStr else { continue }
			out.append(str)
		}
		return out
	}
}


if inFiles == ["-"] {
	print(stringFinder(data: FileHandle.standardInput.readDataToEndOfFile()).joined(separator: "\n"))
}
else {
	for path in inFiles {
		guard FileManager.default.fileExists(atPath: path) else {
			fatalError("No file exists at \(path)")
		}
	}
	for path in inFiles {
		let data = try Data(contentsOf: URL(fileURLWithPath: path))
		print(stringFinder(data: data).joined(separator: "\n"))
	}
}
