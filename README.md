# Regular Expression Parser & Lexical Analyzer

A Python implementation of a regular expression parser that builds Non-deterministic Finite Automata (NFA) for token definitions and performs lexical analysis on input text.

## Overview

This project implements a complete lexical analysis system that:
- **Parses** regular expression definitions using a context-free grammar
- **Constructs** NFA representations for each token pattern
- **Performs** lexical analysis by matching input strings against the NFAs using epsilon-closure and character transitions
- **Validates** for semantic errors (duplicate token declarations) and syntax errors in expressions

## Project Structure

### Core Files

- **`lexer.py`** — Lexical analyzer that tokenizes input into predefined token types (ID, LPAREN, RPAREN, DOT, STAR, OR, UNDERSCORE, CHAR, etc.). Handles whitespace and line tracking.

- **`inputbuf.py`** — Input buffer manager providing character-level I/O with lookahead support via character/string pushback operations (GetChar, UngetChar, UngetString).

- **`parser.py`** — Expression parser and NFA builder. Parses token definitions, constructs NFA graphs, performs semantic validation, and executes lexical analysis using NFA pattern matching.

## Usage

```bash
python3 parser.py < input.txt
```

### Input Format

The input should follow this structure:

```
TOKEN1 (regex_expr1);
TOKEN2 (regex_expr2);
# 
"input_string_to_analyze"
```

**Example:**
```
DIGIT (0|1|2|3|4|5|6|7|8|9);
LETTER (a|b|c|...|z|A|B|C|...|Z);
#
"hello123world"
```

## Supported Operators

- **`.`** — Concatenation: `(a).(b)` matches "ab"
- **`|`** — Alternation (OR): `(a)|(b)` matches "a" or "b"  
- **`*`** — Kleene star: `(a)*` matches zero or more "a"s
- **`_`** — Epsilon (empty string)

## Requirements

- Python 3.6+
- No external dependencies

## Examples

### Syntax Error Example

**Input (invalid regex syntax):**
```
t1 (a)|(b);
t2 (a).((a)*);
t3 (((a)|b)*).(c);
#
"aabac"
```

**Output:**
```
t3 has a syntax error in its expression.
```

### Semantic Error Example

**Input (duplicate token declaration):**
```
t1 (a)|(b);
t1 (a).((a)*);
t2 (((a)|(b))*).(c);
#
"ababc"
```

**Output:**
```
Line 2: t1 already declared on line 1
```

### Successful Lexical Analysis

**Input (valid tokens and input):**
```
t1 (a)|(b);
t2 (a).((a)*);
t3 (((a)|(b))*).(c);
#
"baaac"
```

**Output:**
```
t1, "b"
t2, "aa"
t3, "ac"

```

## Error Handling

- **SYNTAX ERROR** — Invalid expression syntax (mismatched parentheses, invalid operators)
- **Duplicate Token Declarations** — Same token name defined multiple times
- **Epsilon Errors** — Tokens that generate epsilon (empty string) are invalid for lexical analysis

## License

MIT License
