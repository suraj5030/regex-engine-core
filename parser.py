from dataclasses import dataclass
import sys

from lexer import LexicalAnalyzer, TokenType


REG_node_register = []
token_register = []
input_text_for_analysis = ""


@dataclass(eq=False)
class REG_node:
    first_neighbor: "REG_node" = None
    first_label: str = ""
    second_neighbor: "REG_node" = None
    second_label: str = ""


@dataclass
class REG:
    start_node: REG_node = None
    accept_node: REG_node = None
    generates_epsilon: bool = False


@dataclass
class Token_name_info:
    lexeme: str
    line_no: int
    token_type: TokenType
    generates_epsilon: bool
    reg: REG


def create_REG_node():
    node = REG_node()
    REG_node_register.append(node)
    return node


def create_REG_char(c):
    reg = REG()
    reg.start_node = create_REG_node()
    reg.accept_node = create_REG_node()
    reg.generates_epsilon = False

    reg.start_node.first_neighbor = reg.accept_node
    reg.start_node.first_label = c
    return reg


def create_REG_epsilon():
    reg = REG()
    reg.start_node = create_REG_node()
    reg.accept_node = create_REG_node()
    reg.generates_epsilon = True

    reg.start_node.first_neighbor = reg.accept_node
    reg.start_node.first_label = "_"
    return reg


def concat_REGS(reg1, reg2):
    reg1.accept_node.first_neighbor = reg2.start_node
    reg1.accept_node.first_label = "_"

    concat_reg = REG()
    concat_reg.start_node = reg1.start_node
    concat_reg.accept_node = reg2.accept_node
    concat_reg.generates_epsilon = reg1.generates_epsilon and reg2.generates_epsilon
    return concat_reg


def OR_REGS(reg1, reg2):
    outer_start = create_REG_node()
    outer_accept = create_REG_node()

    outer_start.first_neighbor = reg1.start_node
    outer_start.second_neighbor = reg2.start_node
    outer_start.first_label = "_"
    outer_start.second_label = "_"

    reg1.accept_node.first_neighbor = outer_accept
    reg1.accept_node.first_label = "_"

    reg2.accept_node.first_neighbor = outer_accept
    reg2.accept_node.first_label = "_"

    reg = REG()
    reg.start_node = outer_start
    reg.accept_node = outer_accept
    reg.generates_epsilon = reg1.generates_epsilon or reg2.generates_epsilon
    return reg


def kleene_star_REG(reg):
    outer_start = create_REG_node()
    outer_accept = create_REG_node()

    outer_start.first_neighbor = reg.start_node
    outer_start.first_label = "_"
    outer_start.second_neighbor = outer_accept
    outer_start.second_label = "_"

    reg.accept_node.first_neighbor = reg.start_node
    reg.accept_node.first_label = "_"

    reg.accept_node.second_neighbor = outer_accept
    reg.accept_node.second_label = "_"

    starred = REG()
    starred.start_node = outer_start
    starred.accept_node = outer_accept
    starred.generates_epsilon = True
    return starred


class Parser:
    def __init__(self):
        self.lexer = LexicalAnalyzer()

    def syntax_error(self):
        print("SYNTAX ERROR", end="")
        raise SystemExit(1)

    def expr_syntax_error(self, token_name):
        print(token_name.lexeme + " has a syntax error in its expression.", end="")
        raise SystemExit(1)

    def expect(self, expected_type):
        t = self.lexer.GetToken()
        if t.token_type != expected_type:
            self.syntax_error()
        return t

    def parse_expr(self, token_name):
        t = self.lexer.peek(1)

        if t.token_type == TokenType.CHAR:
            ch = self.expect(TokenType.CHAR)
            return create_REG_char(ch.lexeme[0])

        if t.token_type == TokenType.UNDERSCORE:
            self.expect(TokenType.UNDERSCORE)
            return create_REG_epsilon()

        if t.token_type == TokenType.LPAREN:
            self.expect(TokenType.LPAREN)
            left = self.parse_expr(token_name)

            if self.lexer.peek(1).token_type != TokenType.RPAREN:
                self.expr_syntax_error(token_name)
            self.expect(TokenType.RPAREN)

            t = self.lexer.peek(1)

            if t.token_type == TokenType.DOT:
                self.expect(TokenType.DOT)
                if self.lexer.peek(1).token_type != TokenType.LPAREN:
                    self.expr_syntax_error(token_name)
                self.expect(TokenType.LPAREN)
                right = self.parse_expr(token_name)
                if self.lexer.peek(1).token_type != TokenType.RPAREN:
                    self.expr_syntax_error(token_name)
                self.expect(TokenType.RPAREN)
                return concat_REGS(left, right)

            if t.token_type == TokenType.OR:
                self.expect(TokenType.OR)
                if self.lexer.peek(1).token_type != TokenType.LPAREN:
                    self.expr_syntax_error(token_name)
                self.expect(TokenType.LPAREN)
                right = self.parse_expr(token_name)
                if self.lexer.peek(1).token_type != TokenType.RPAREN:
                    self.expr_syntax_error(token_name)
                self.expect(TokenType.RPAREN)
                return OR_REGS(left, right)

            if t.token_type == TokenType.STAR:
                self.expect(TokenType.STAR)
                return kleene_star_REG(left)

            self.expr_syntax_error(token_name)

        self.expr_syntax_error(token_name)

    def parse_token(self):
        t = self.lexer.peek(1)
        if t.token_type == TokenType.ID:
            token_name = self.expect(TokenType.ID)
            parsed = self.parse_expr(token_name)

            tok_decl = Token_name_info(
                lexeme=token_name.lexeme,
                line_no=token_name.line_no,
                token_type=token_name.token_type,
                generates_epsilon=parsed.generates_epsilon,
                reg=parsed,
            )
            token_register.append(tok_decl)
        else:
            self.syntax_error()

    def parse_token_list(self):
        self.parse_token()
        t = self.lexer.peek(1)
        if t.token_type == TokenType.SEMICOLON:
            self.expect(TokenType.SEMICOLON)
            self.parse_token_list()
        elif t.token_type == TokenType.HASH:
            return
        else:
            self.syntax_error()

    def parse_tokens_section(self):
        self.parse_token_list()
        if self.lexer.peek(1).token_type != TokenType.HASH:
            self.syntax_error()
        self.expect(TokenType.HASH)

    def parse_input(self):
        global input_text_for_analysis
        self.parse_tokens_section()
        input_token = self.expect(TokenType.INPUT_TEXT)
        input_text_for_analysis = input_token.lexeme
        self.expect(TokenType.END_OF_FILE)

    def readAndPrintAllInput(self):
        t = self.lexer.GetToken()
        while t.token_type != TokenType.END_OF_FILE:
            t.Print()
            t = self.lexer.GetToken()

    def print_semantic_errors(self):
        semantic_error_message = ""

        for i in range(len(token_register)):
            for j in range(i):
                if token_register[i].lexeme == token_register[j].lexeme:
                    semantic_error_message += (
                        "Line "
                        + str(token_register[i].line_no)
                        + ": "
                        + token_register[i].lexeme
                        + " already declared on line "
                        + str(token_register[j].line_no)
                        + "\n"
                    )
                    break

        if semantic_error_message:
            print(semantic_error_message, end="")
            raise SystemExit(1)

    def print_epsilon_errors(self):
        output = ""

        for tok in token_register:
            if tok.generates_epsilon:
                if output:
                    output += " "
                output += tok.lexeme

        if output:
            print("Error: epsilon is not a valid token. The following token(s) generate epsilon: " + output)
            raise SystemExit(1)


def epsilon_transition(S):
    changed = True
    S_1 = set(S)

    while changed:
        changed = False
        S_2 = set()

        for n in S_1:
            S_2.add(n)

            if n.first_neighbor is not None and n.first_label == "_":
                if n.first_neighbor not in S_2:
                    S_2.add(n.first_neighbor)

            if n.second_neighbor is not None and n.second_label == "_":
                if n.second_neighbor not in S_2:
                    S_2.add(n.second_neighbor)

        if S_1 != S_2:
            changed = True
            S_1 = S_2

    return S_1


def match_one_char(S, c):
    S_start = epsilon_transition(S)

    S_prime = set()
    for n in S_start:
        if n.first_neighbor is not None and n.first_label == c:
            S_prime.add(n.first_neighbor)
        if n.second_neighbor is not None and n.second_label == c:
            S_prime.add(n.second_neighbor)

    if not S_prime:
        return S_prime

    return epsilon_transition(S_prime)


def match(r, s, p):
    S = {r.start_node}
    S = epsilon_transition(S)

    last_match = -1
    if r.accept_node in S:
        last_match = p

    i = p
    while i < len(s) and S:
        c = s[i]
        S = match_one_char(S, c)

        if not S:
            break

        if r.accept_node in S:
            last_match = i

        i += 1

    return last_match


def perform_lexical_analysis(input_text):
    if len(input_text) >= 2 and input_text[0] == '"' and input_text[-1] == '"':
        input_text = input_text[1:-1]

    pos = 0
    while pos < len(input_text):
        if input_text[pos] == " ":
            pos += 1
            continue

        best_match_length = -1
        best_token_index = -1

        for i in range(len(token_register)):
            match_end = match(token_register[i].reg, input_text, pos)
            if match_end >= pos:
                match_length = match_end - pos + 1
                if match_length > best_match_length:
                    best_match_length = match_length
                    best_token_index = i

        if best_token_index == -1:
            print("Error: no valid token could be matched for the current input.")
            return

        lexeme = input_text[pos : pos + best_match_length]
        print(token_register[best_token_index].lexeme + ", \"" + lexeme + "\"")
        pos += best_match_length

    print()


def main():
    parser = Parser()
    parser.parse_input()
    parser.print_semantic_errors()
    parser.print_epsilon_errors()
    perform_lexical_analysis(input_text_for_analysis)


if __name__ == "__main__":
    main()
