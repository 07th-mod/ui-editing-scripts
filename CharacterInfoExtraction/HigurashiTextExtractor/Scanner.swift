//
//  Scanner.swift
//  CParser_CS440
//

import Foundation

enum TokenType: String {
	case stringLiteral, characterLiteral, punctuation, identifier
}

enum TokenizationError: Error {
	case badPunctuation(row: Int, column: Int, character: UnicodeScalar)
	case unclosedString(row: Int, column: Int, string: String)
}

struct TokenListSignature: Hashable, Equatable {
	let list: [TokenType]
	init(_ array: [TokenType]) {
		self.list = array
	}
	init(from tokens: [Token]) {
		list = tokens.map { $0.type }
	}
	static func ==(lhs: TokenListSignature, rhs: TokenListSignature) -> Bool {
		guard lhs.list.count == rhs.list.count else { return false }
		for tokentype in lhs.list.enumerated() {
			if rhs.list[tokentype.offset] != tokentype.element {
				return false
			}
		}
		return true
	}
	var hashValue: Int {
		return list.map({ $0.hashValue }).reduce(5381) {
			($0 << 5) &+ $0 &+ $1
		}
	}
}

struct MovingStringRange {
	let string: String.UnicodeScalarView
	private(set) var back: String.UnicodeScalarIndex
	private(set) var front: String.UnicodeScalarIndex
	private(set) var length: Int
	private(set) var backRow: Int
	private(set) var backColumn: Int
	private(set) var frontRow: Int
	private(set) var frontColumn: Int
	init(_ string: String.UnicodeScalarView, atEnd: Bool = false) {
		self.string = string
		self.length = 0
		self.back = atEnd ? string.endIndex : string.startIndex
		self.front = back
		self.backRow = 1
		self.backColumn = 1
		self.frontRow = 1
		self.frontColumn = 1
	}
	init(_ string: String, atEnd: Bool = false) {
		self.init(string.unicodeScalars, atEnd: atEnd)
	}
	private mutating func advanceFront() {
		if frontChar == "\n" {
			frontColumn = 1
			frontRow += 1
		}
		else {
			frontColumn += 1
		}
		front = string.index(after: front)
		length += 1
	}
	private mutating func retreatFront() {
		front = string.index(before: front)
		length -= 1
		if frontChar == "\n" {
			var check = string.index(before: front)
			frontColumn = 2
			while check >= string.startIndex && string[check] != "\n" {
				frontColumn += 1
				check = string.index(before: check)
			}
			frontRow -= 1
		}
		else {
			frontColumn -= 1
		}
	}
	mutating func advanceFront(by: Int = 1) {
		if by > 0 {
			for _ in 0..<by {
				advanceFront()
			}
		}
		else {
			for _ in 0..<(-by) {
				retreatFront()
			}
		}
	}
	private mutating func advanceBack() {
		if backChar == "\n" {
			backColumn = 1
			backRow += 1
		}
		else {
			backColumn += 1
		}
		back = string.index(after: back)
		length += 1
	}
	private mutating func retreatBack() {
		back = string.index(before: back)
		length -= 1
		if backChar == "\n" {
			var check = string.index(before: back)
			backColumn = 2
			while check >= string.startIndex && string[check] != "\n" {
				backColumn += 1
				check = string.index(before: check)
			}
			backRow -= 1
		}
		else {
			backColumn -= 1
		}
	}
	mutating func advanceBack(by: Int = 1) {
		if by > 0 {
			for _ in 0..<by {
				advanceBack()
			}
		}
		else {
			for _ in 0..<(-by) {
				retreatBack()
			}
		}
	}
	mutating func setBackToFront() {
		back = front
		backColumn = frontColumn
		backRow = frontRow
		length = 0
	}
	mutating func setFrontToBack() {
		front = back
		frontColumn = backColumn
		frontRow = backRow
		length = 0
	}
	var currentRange: String {
		return String(string[back..<front])
	}
	var frontChar: UnicodeScalar {
		return string[front]
	}
	var backChar: UnicodeScalar {
		return string[back]
	}
	var backIsBeginning: Bool {
		return back <= string.startIndex
	}
	var backIsEnd: Bool {
		return back >= string.endIndex
	}
	var frontIsBeginning: Bool {
		return front <= string.startIndex
	}
	var frontIsEnd: Bool {
		return front >= string.endIndex
	}
}

extension UnicodeScalar {
	var isNewline: Bool {
		return (0x0a...0x0d).contains(self.value) || self.value == 0x85 || self.value == 0x2028 || self.value == 0x2029
	}
	var isWhitespace: Bool {
		return self.value == 0x20 || self.value == 0xa0 || self.value == 0x1680 || (0x2000...0x200a).contains(self.value) || self.value == 0x202f || self.value == 0x205f || self.value == 0x3000
	}
	var isNewlineOrWhitespace: Bool {
		return isNewline || isWhitespace
	}
}

struct Token: CustomStringConvertible {
	let type: TokenType
	let value: String
	let row: Int
	let column: Int
	init(type: TokenType, value: String, row: Int, column: Int) {
		self.type = type
		self.value = value
		self.row = row
		self.column = column
	}
	init(type: TokenType, value: String.UnicodeScalarView, row: Int, column: Int) {
		self.init(type: type, value: String(value), row: row, column: column)
	}
	var description: String {
//		return "[\(type) \(value)]"
		switch type {
		case .identifier, .punctuation:
			return value
		case .stringLiteral:
			return "\"\(value)\""
		case .characterLiteral:
			return "'\(value)'"
		}
	}
	
	static func tokenize(input: String) throws -> [Token] {
		var inputRange = MovingStringRange(input)
		var tokens: [Token] = []
		
		while !inputRange.backIsEnd {
			//print("Currently looking from row \(inputRange.backRow) column \(inputRange.backColumn) to row \(inputRange.frontRow) column \(inputRange.frontColumn), \(inputRange.currentRange)")
			if inputRange.frontIsEnd { // If this is the end of the file
				if (inputRange.length > 0) {
					tokens.append(Token(type: .identifier, value: inputRange.currentRange, row: inputRange.backRow, column: inputRange.backColumn))
				}
				inputRange.setBackToFront()
				continue
			}
			else if inputRange.frontChar.isNewlineOrWhitespace { // Whitespace, end of token
				if inputRange.length > 0 { // If there's multiple whitespace chars in a row, don't add empty tokens
					tokens.append(Token(type: .identifier, value: inputRange.currentRange, row: inputRange.backRow, column: inputRange.backColumn))
				}
				inputRange.advanceFront()
				inputRange.setBackToFront()
			}
			else if punctuationCharacters.contains(inputRange.frontChar) {
				if inputRange.length > 0 { // Add the previous identifier if it exists
					tokens.append(Token(type: .identifier, value: inputRange.currentRange, row: inputRange.backRow, column: inputRange.backColumn))
				}
				inputRange.setBackToFront()
				while !inputRange.frontIsEnd && (punctuationCharacters.contains(inputRange.frontChar) || inputRange.length > 0) {
					// Keep going until we reach the end of the file and have parsed it all
					inputRange.advanceFront()
					if inputRange.length > longestPunctuation || inputRange.frontIsEnd || !punctuationCharacters.contains(inputRange.frontChar) {
						var punctuationToken = inputRange.currentRange
						while inputRange.length > 1 && !allPunctuation.contains(punctuationToken) {
							inputRange.advanceFront(by: -1)
							punctuationToken = inputRange.currentRange
						}
						if commentPunctuation.contains(punctuationToken) {
							if punctuationToken == "//" {
								while !inputRange.frontIsEnd && !inputRange.frontChar.isNewline {
									inputRange.advanceFront()
								}
							}
							else {
								while !inputRange.frontIsEnd && inputRange.frontChar != "/" {
									while !inputRange.frontIsEnd && inputRange.frontChar != "*" {
										inputRange.advanceFront()
									}
									inputRange.advanceFront()
								}
							}
							inputRange.advanceFront()
							inputRange.setBackToFront()
							continue
						}
						if allPunctuation.contains(punctuationToken) {
							tokens.append(Token(type: .punctuation, value: punctuationToken, row: inputRange.backRow, column: inputRange.backColumn))
							inputRange.setBackToFront()
						}
						else {
							throw TokenizationError.badPunctuation(row: inputRange.backRow, column: inputRange.backColumn, character: inputRange.backChar)
						}
					}
				}
			}
			else if inputRange.frontChar == "\"" || inputRange.frontChar == "'" {
				let quoteType = inputRange.frontChar
				if inputRange.length > 0 { // Add the previous identifier if it exists
					tokens.append(Token(type: .identifier, value: inputRange.currentRange, row: inputRange.backRow, column: inputRange.backColumn))
				}
				inputRange.advanceFront()
				inputRange.setBackToFront()
				while true {
					if inputRange.frontIsEnd || inputRange.frontChar.isNewline {
						inputRange.advanceBack(by: -1)
						throw TokenizationError.unclosedString(row: inputRange.backRow, column: inputRange.backColumn, string: inputRange.currentRange)
					}
					else if inputRange.frontChar == "\\" {
						inputRange.advanceFront(by: 2)
					}
					else if inputRange.frontChar == quoteType {
						let type: TokenType
						if quoteType == "'" {
							type = .characterLiteral
						}
						else {
							type = .stringLiteral
						}
						tokens.append(Token(type: type, value: inputRange.currentRange, row: inputRange.backRow, column: inputRange.backColumn - 1))
						inputRange.advanceFront()
						inputRange.setBackToFront()
						break
					}
					else {
						inputRange.advanceFront()
					}
				}
			}
			else {
				inputRange.advanceFront()
			}
		}
		return tokens
	}
}
