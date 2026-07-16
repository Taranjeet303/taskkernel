from enum import Enum, auto

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()
    IDENTIFIER = auto()

    # Keywords — structural
    FLOW = auto()
    TASK = auto()
    STEP = auto()
    ON_FAIL = auto()

    # Keywords — statements / control flow
    LET = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    RETURN = auto()

    # Keywords — literals / logical
    TRUE = auto()
    FALSE = auto()
    AND = auto()
    OR = auto()
    NOT = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    EQ = auto()          # =
    EQ_EQ = auto()        # ==
    NOT_EQ = auto()       # !=
    LT = auto()
    GT = auto()
    LT_EQ = auto()
    GT_EQ = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    COLON = auto()        # type annotations + record key:value
    DOT = auto()          # member access, e.g. response.status
    
    #specials
    NEWLINE = auto()
    EOF = auto()


class Token:
    def __init__(self, type_: TokenType, lexeme: str, literal, line: int, col: int):
        self.type = type_
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {self.lexeme!r}, line={self.line}, col={self.col})"


KEYWORDS = {
    "flow": TokenType.FLOW,
    "task": TokenType.TASK,
    "step": TokenType.STEP,
    "on_fail": TokenType.ON_FAIL,
    "let": TokenType.LET,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "return": TokenType.RETURN,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "not": TokenType.NOT,
}