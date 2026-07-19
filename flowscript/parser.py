from .tokens import Token, TokenType
from .ast_nodes import (
    NumberLiteral, StringLiteral, BooleanLiteral, ListLiteral,
    RecordLiteral, Identifier, BinaryOp, UnaryOp, Call, MemberAccess
)


class ParseError(Exception):
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"Parse error at line {line}, col {col}: {message}")


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # ---------- token stream helpers ----------

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def previous(self) -> Token:
        return self.tokens[self.pos - 1]

    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def check(self, type_: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == type_

    def advance(self) -> Token:
        if not self.is_at_end():
            self.pos += 1
        return self.previous()

    def match(self, *types: TokenType) -> bool:
        for t in types:
            if self.check(t):
                self.advance()
                return True
        return False

    def consume(self, type_: TokenType, message: str) -> Token:
        if self.check(type_):
            return self.advance()
        tok = self.peek()
        raise ParseError(message, tok.line, tok.col)

    # ---------- expression grammar (precedence climbing) ----------
    # Mirrors GRAMMAR.md Section 15 exactly, lowest to highest precedence.

    def expression(self):
        return self.logical_or()

    def logical_or(self):
        expr = self.logical_and()
        while self.match(TokenType.OR):
            op_tok = self.previous()
            right = self.logical_and()
            expr = BinaryOp(expr, "or", right, op_tok.line, op_tok.col)
        return expr

    def logical_and(self):
        expr = self.equality()
        while self.match(TokenType.AND):
            op_tok = self.previous()
            right = self.equality()
            expr = BinaryOp(expr, "and", right, op_tok.line, op_tok.col)
        return expr

    def equality(self):
        expr = self.comparison()
        while self.match(TokenType.EQ_EQ, TokenType.NOT_EQ):
            op_tok = self.previous()
            right = self.comparison()
            expr = BinaryOp(expr, op_tok.lexeme, right, op_tok.line, op_tok.col)
        return expr

    def comparison(self):
        expr = self.term()
        while self.match(TokenType.LT, TokenType.GT, TokenType.LT_EQ, TokenType.GT_EQ):
            op_tok = self.previous()
            right = self.term()
            expr = BinaryOp(expr, op_tok.lexeme, right, op_tok.line, op_tok.col)
        return expr

    def term(self):
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op_tok = self.previous()
            right = self.factor()
            expr = BinaryOp(expr, op_tok.lexeme, right, op_tok.line, op_tok.col)
        return expr

    def factor(self):
        expr = self.unary()
        while self.match(TokenType.STAR, TokenType.SLASH):
            op_tok = self.previous()
            right = self.unary()
            expr = BinaryOp(expr, op_tok.lexeme, right, op_tok.line, op_tok.col)
        return expr

    def unary(self):
        if self.match(TokenType.NOT, TokenType.MINUS):
            op_tok = self.previous()
            operand = self.unary()
            return UnaryOp(op_tok.lexeme, operand, op_tok.line, op_tok.col)
        return self.call()

   