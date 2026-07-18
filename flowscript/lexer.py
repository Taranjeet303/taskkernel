from flowscript.tokens import Token, TokenType, KEYWORDS


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []

    def tokenize(self) -> list[Token]:
        while not self.is_at_end():
            self.scan_token()

        self.tokens.append(
            Token(
                TokenType.EOF,
                "",
                None,
                self.line,
                self.col
            )
        )

        return self.tokens

    def is_at_end(self) -> bool:
        return self.pos >= len(self.source)

    def peek(self) -> str:
        if self.is_at_end():
            return "\0"

        return self.source[self.pos]

    def advance(self) -> str:
        char = self.source[self.pos]

        self.pos += 1

        if char == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1

        return char

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False

        if self.source[self.pos] != expected:
            return False

        self.pos += 1
        self.col += 1
        return True

    def add_token(self, token_type: TokenType, lexeme: str, literal=None):
        token = Token(
            token_type,
            lexeme,
            literal,
            self.line,
            self.col - len(lexeme)
        )

        self.tokens.append(token)

    def scan_token(self):
        char = self.advance()

        match char:

            # ------------------------
            # Whitespace
            # ------------------------

            case " " | "\t" | "\r":
                return

            case "\n":
                self.add_token(TokenType.NEWLINE, "\n")

            # ------------------------
            # Single-character tokens
            # ------------------------

            case "(":
                self.add_token(TokenType.LPAREN, "(")

            case ")":
                self.add_token(TokenType.RPAREN, ")")

            case "{":
                self.add_token(TokenType.LBRACE, "{")

            case "}":
                self.add_token(TokenType.RBRACE, "}")

            case "[":
                self.add_token(TokenType.LBRACKET, "[")

            case "]":
                self.add_token(TokenType.RBRACKET, "]")

            case ",":
                self.add_token(TokenType.COMMA, ",")

            case ":":
                self.add_token(TokenType.COLON, ":")

            case ".":
                self.add_token(TokenType.DOT, ".")

            case "+":
                self.add_token(TokenType.PLUS, "+")

            case "-":
                self.add_token(TokenType.MINUS, "-")

            case "*":
                self.add_token(TokenType.STAR, "*")

            # ------------------------
            # Multi-character operators
            # ------------------------

            case "=":
                if self.match("="):
                    self.add_token(TokenType.EQ_EQ, "==")
                else:
                    self.add_token(TokenType.EQ, "=")

            case "!":
                if self.match("="):
                    self.add_token(TokenType.NOT_EQ, "!=")
                else:
                    raise SyntaxError(
                        f"Unexpected character '!' at line {self.line}"
                    )

            case "<":
                if self.match("="):
                    self.add_token(TokenType.LT_EQ, "<=")
                else:
                    self.add_token(TokenType.LT, "<")

            case ">":
                if self.match("="):
                    self.add_token(TokenType.GT_EQ, ">=")
                else:
                    self.add_token(TokenType.GT, ">")

            # ------------------------
            # Slash or comment
            # ------------------------

            case "/":
                self.add_token(TokenType.SLASH, "/")

            case "#":
                while not self.is_at_end() and self.peek() != "\n":
                    self.advance()

            # ------------------------
            # Literals
            # ------------------------

            case '"':
                self.string()

            case _:

                if char.isdigit():
                    self.number()

                elif char.isalpha() or char == "_":
                    self.identifier()

                else:
                    raise SyntaxError(
                        f"Unexpected character '{char}' "
                        f"at line {self.line}, column {self.col}"
                    )
                
    def string(self):
                    start_line = self.line
                    start_col = self.col - 1

                    value = ""

                    while not self.is_at_end() and self.peek() != '"':
                        value += self.advance()

                    if self.is_at_end():
                        raise SyntaxError(
                            f"Unterminated string at line {start_line}, column {start_col}"
                        )

                    # Consume closing quote
                    self.advance()

                    self.tokens.append(
                        Token(
                            TokenType.STRING,
                            f'"{value}"',
                            value,
                            start_line,
                            start_col
                        )
                    )

    def number(self):
                start_line = self.line
                start_col = self.col - 1

                lexeme = self.source[self.pos - 1]

                while self.peek().isdigit():
                    lexeme += self.advance()

                # Decimal numbers
                if self.peek() == "." and self.pos + 1 < len(self.source):
                    if self.source[self.pos + 1].isdigit():
                        lexeme += self.advance()  # consume '.'

                        while self.peek().isdigit():
                            lexeme += self.advance()

                literal = float(lexeme) if "." in lexeme else int(lexeme)

                self.tokens.append(
                    Token(
                        TokenType.NUMBER,
                        lexeme,
                        literal,
                        start_line,
                        start_col
                    )
                )

    def identifier(self):
                start_line = self.line
                start_col = self.col - 1

                lexeme = self.source[self.pos - 1]

                while self.peek().isalnum() or self.peek() == "_":
                    lexeme += self.advance()

                token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)

                literal = None
                if token_type == TokenType.TRUE:
                    literal = True
                elif token_type == TokenType.FALSE:
                    literal = False

                self.tokens.append(
                    Token(
                        token_type,
                        lexeme,
                        literal,
                        start_line,
                        start_col
                    )
                )            