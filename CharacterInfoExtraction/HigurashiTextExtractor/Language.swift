//
//  Language.swift
//  CParser_CS440
//

import Foundation

enum Associativity {
	case left, right;
}

var typeNames: Set<String> = ["bool", "char", "short", "int", "long", "float", "double"]

var convertibleTypes: [Set<String>] = [["bool", "char", "short", "int", "long"], ["float", "double"]]

func isConvertible(left: String, right: String) -> Bool {
	for convertibleSet in convertibleTypes {
		if convertibleSet.contains(left) && convertibleSet.contains(right) {
			return true
		}
	}
	return false
}

enum Type: CustomStringConvertible {
	case any, noType, specific(String)
	var description: String {
		switch self {
		case .specific(let string):
			return string
		case .noType:
			return "None"
		case .any:
			return "Any"
		}
	}
}

let binaryOperators: Dictionary<Int, (Associativity, Set<String>)> = [
	160: (.left, ["<<", ">>"]),
	150: (.left, ["*", "/", "%", "&"]),
	140: (.left, ["+", "-", "|", "^"]),
	130: (.left, ["<", "<=", ">", ">=", "==", "!="]),
	120: (.left, ["&&"]),
	110: (.left, ["||"])
]

let allIntegersBinaryOperator: [(left: Type, right: Type, out: Type)] = [(left: .specific("int"), right: .specific("int"), out: .specific("int"))]
let allNumbersBinaryOperator: [(left: Type, right: Type, out: Type)] = [(left: .specific("int"), right: .specific("int"), out: .specific("int")), (left: .specific("double"), right: .specific("double"), out: .specific("double")), (left: .specific("float"), right: .specific("float"), out: .specific("float"))]
let allBooleansBinaryOperator: [(left: Type, right: Type, out: Type)] = [(left: .specific("bool"), right: .specific("bool"), out: .specific("bool"))]
let comparisonBinaryOperator: [(left: Type, right: Type, out: Type)] = [(left: .any, right: .any, out: .specific("bool"))]

let binaryOperatorTypes: Dictionary<String, [(left: Type, right: Type, out: Type)]> = [
	"<<": allIntegersBinaryOperator,
	">>": allIntegersBinaryOperator,
	"*": allNumbersBinaryOperator,
	"/": allNumbersBinaryOperator,
	"%": allIntegersBinaryOperator,
	"&": allIntegersBinaryOperator,
	"+": allNumbersBinaryOperator,
	"-": allNumbersBinaryOperator,
	"|": allIntegersBinaryOperator,
	"^": allIntegersBinaryOperator,
	"<": comparisonBinaryOperator,
	"<=": comparisonBinaryOperator,
	">": comparisonBinaryOperator,
	">=": comparisonBinaryOperator,
	"==": comparisonBinaryOperator,
	"!=": comparisonBinaryOperator,
	"&&": allBooleansBinaryOperator,
	"||": allBooleansBinaryOperator
]

let assignmentOperators: Set<String> = ["=", "*=", "/=", "%=", "+=", "-=", "<<=", ">>=", "&=", "^=", "|="]

let assignmentOperatorTypes: Dictionary<String, [Type]> = [
	"=": [.any],
	"*=": [.specific("int"), .specific("double"), .specific("float")],
	"/=": [.specific("int"), .specific("double"), .specific("float")],
	"%=": [.specific("int")],
	"+=": [.specific("int"), .specific("double"), .specific("float")],
	"-=": [.specific("int"), .specific("double"), .specific("float")],
	"<<=": [.specific("int")],
	">>=": [.specific("int")],
	"&=": [.specific("int")],
	"^=": [.specific("int")],
	"|=": [.specific("int")]
]

let prefixOperators: Set<String> = ["!", "~", "++", "--", "+", "-"]
let postfixOperators: Set<String> = ["++", "--"]


let allIntegersUnaryOperator: [(in: Type, out: Type)] = [(in: .specific("int"), out: .specific("int"))]
let allNumbersUnaryOperator: [(in: Type, out: Type)] = [(in: .specific("int"), out: .specific("int")), (in: .specific("double"), out: .specific("double")), (in: .specific("float"), out: .specific("float"))]
let allBooleansUnaryOperator: [(in: Type, out: Type)] = [(in: .specific("bool"), out: .specific("bool"))]

let unaryOperatorTypes: Dictionary<String, [(in: Type, out: Type)]> = [
	"!": allBooleansUnaryOperator,
	"~": allIntegersUnaryOperator,
	"++": allNumbersUnaryOperator,
	"--": allNumbersUnaryOperator,
	"+": allNumbersUnaryOperator,
	"-": allNumbersUnaryOperator
]

let otherPunctuation: Set<String> = ["(", ")", "{", "}", "[", "]", ";", ",", "."]
let commentPunctuation: Set<String> = ["//", "/*"]

let allPunctuation: Set<String> = prefixOperators.union(postfixOperators).union(assignmentOperators).union(binaryOperators.values.flatMap({$0.1})).union(otherPunctuation).union(commentPunctuation)
let punctuationCharacters = Set(allPunctuation.flatMap({ $0.unicodeScalars }))
let longestPunctuation = allPunctuation.reduce(0, { longest, current in let len = current.count; return len > longest ? len : longest })
let nonIdentifierCharacters = punctuationCharacters.union(["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"])

