from dataclasses import dataclass
from enum import IntEnum
import sys

from inputbuf import InputBuffer


class TokenType(IntEnum):
    END_OF_FILE = 0
    LPAREN = 1
    RPAREN = 2
    HASH = 3
    ID = 4
    SEMICOLON = 5
    DOT = 6
    STAR = 7
    OR = 8
    UNDERSCORE = 9
    SYMBOL = 10
    CHAR = 11
    INPUT_TEXT = 12
    ERROR = 13


RESERVED = [
    "END_OF_FILE",
    "LPAREN",
    "RPAREN",
    "HASH",
    "ID",
    "SEMICOLON",
    "DOT",
    "STAR",
    "OR",
    "UNDERSCORE",
    "SYMBOL",
    "CHAR",
    "INPUT_TEXT",
    "ERROR",
]


@dataclass
class Token:
    lexeme: str = ""
    token_type: TokenType = TokenType.ERROR
    line_no: int = 1

    def Print(self):
        print("{" + self.lexeme + " , " + RESERVED[int(self.token_type)] + " , " + str(self.line_no) + "}")


class LexicalAnalyzer:
    def __init__(self, data=None):
        self.line_no = 1
        self.tmp = Token("", TokenType.ERROR, 1)
        self.input = InputBuffer(data if data is not None else sys.stdin.read())
        self.tokenList = []

        token = self.GetTokenMain()
        self.index = 0
        while token.token_type != TokenType.END_OF_FILE:
            self.tokenList.append(token)
            token = self.GetTokenMain()

    def SkipSpace(self):
        space_encountered = False
        c = self.input.GetChar()
        while c and c.isspace():
            space_encountered = True
            if c == "\n":
                self.line_no += 1
            c = self.input.GetChar()

        if c:
            self.input.UngetChar(c)
        return space_encountered

    def ScanIdOrChar(self):
        c = self.input.GetChar()
        if c and c.isalpha():
            lexeme = ""
            no = 0
            while c and c.isalnum():
                lexeme += c
                c = self.input.GetChar()
                no += 1

            self.tmp.lexeme = lexeme
            self.tmp.line_no = self.line_no
            self.tmp.token_type = TokenType.CHAR if no == 1 else TokenType.ID

            if c:
                self.input.UngetChar(c)
        else:
            if c:
                self.input.UngetChar(c)
            self.tmp.lexeme = ""
            self.tmp.token_type = TokenType.ERROR
        return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)

    def ScanSymbol(self):
        c = self.input.GetChar()
        self.tmp.lexeme = ""

        if c and (c.isspace() or c.isalnum()):
            lexeme = ""
            while c and (c.isspace() or c.isalnum()):
                if c == "\n":
                    self.line_no += 1
                lexeme += c
                c = self.input.GetChar()

            if c:
                self.input.UngetChar(c)

            self.tmp.lexeme = lexeme
            self.tmp.line_no = self.line_no
            self.tmp.token_type = TokenType.SYMBOL
        else:
            if c:
                self.input.UngetChar(c)
            self.tmp.lexeme = ""
            self.tmp.token_type = TokenType.ERROR

        return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)

    def ScanInput(self):
        c = self.input.GetChar()
        if c == '"':
            lexeme = '"'
            self.tmp.lexeme = ""
            symbol = self.ScanSymbol()

            while symbol.token_type == TokenType.SYMBOL:
                lexeme += symbol.lexeme
                symbol = self.ScanSymbol()

            if not self.input.EndOfInput():
                c = self.input.GetChar()
                if c == '"':
                    lexeme += c
                    self.tmp.lexeme += lexeme
                    self.tmp.token_type = TokenType.INPUT_TEXT
                else:
                    self.tmp.lexeme = ""
                    self.tmp.token_type = TokenType.ERROR
            else:
                self.tmp.lexeme = ""
                self.tmp.token_type = TokenType.ERROR

            self.tmp.line_no = self.line_no
        else:
            if c:
                self.input.UngetChar(c)
            self.tmp.lexeme = ""
            self.tmp.token_type = TokenType.ERROR

        return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)

    def GetToken(self):
        if self.index == len(self.tokenList):
            return Token("", TokenType.END_OF_FILE, self.line_no)

        token = self.tokenList[self.index]
        self.index += 1
        return token

    def peek(self, howFar):
        if howFar <= 0:
            print("LexicalAnalyzer.peek error: argument must be a positive integer.")
            raise SystemExit(-1)

        peekIndex = self.index + howFar - 1
        if peekIndex > (len(self.tokenList) - 1):
            return Token("", TokenType.END_OF_FILE, self.line_no)
        return self.tokenList[peekIndex]

    def GetTokenMain(self):
        self.SkipSpace()
        self.tmp.lexeme = ""
        self.tmp.line_no = self.line_no
        self.tmp.token_type = TokenType.END_OF_FILE

        if self.input.EndOfInput():
            return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)

        c = self.input.GetChar()

        if c == '(':
            self.tmp.token_type = TokenType.LPAREN
            return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)
        if c == ')':
            self.tmp.token_type = TokenType.RPAREN
            return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)
        if c == ';':
            self.tmp.token_type = TokenType.SEMICOLON
            return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)
        if c == '.':
            self.tmp.token_type = TokenType.DOT
            return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)
        if c == '*':
            self.tmp.token_type = TokenType.STAR
            return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)
        if c == '|':
            self.tmp.token_type = TokenType.OR
            return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)
        if c == '#':
            self.tmp.token_type = TokenType.HASH
            return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)
        if c == '_':
            self.tmp.token_type = TokenType.UNDERSCORE
            return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)
        if c == '"':
            self.input.UngetChar(c)
            return self.ScanInput()

        if c and c.isdigit():
            self.tmp.token_type = TokenType.CHAR
            self.tmp.lexeme = c
        elif c and c.isalpha():
            self.input.UngetChar(c)
            return self.ScanIdOrChar()
        elif self.input.EndOfInput():
            self.tmp.token_type = TokenType.END_OF_FILE
        else:
            self.tmp.token_type = TokenType.ERROR

        return Token(self.tmp.lexeme, self.tmp.token_type, self.tmp.line_no)
