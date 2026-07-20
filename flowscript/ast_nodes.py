from dataclasses import dataclass


class Expr:
    """Base class for all expression AST nodes."""
    pass

@dataclass
class NumberLiteral(Expr):
    value: int | float
    line: int
    col: int

@dataclass
class StringLiteral(Expr):
    value: str
    line: int
    col: int

@dataclass
class BooleanLiteral(Expr):
    value: bool
    line: int
    col: int

@dataclass
class Identifier(Expr):
    name: str
    line: int
    col: int

@dataclass
class BinaryOp(Expr):
    left: Expr
    operator: str
    right: Expr
    line: int
    col: int

@dataclass
class UnaryOp(Expr):
    operator: str
    operand: Expr
    line: int
    col: int

@dataclass
class Call(Expr):
    callee: Expr
    arguments: list[Expr]
    line: int
    col: int

@dataclass
class MemberAccess(Expr):
    object: Expr
    member: str
    line: int
    col: int                        

@dataclass
class ListLiteral(Expr):
    elements: list[Expr]
    line: int
    col: int

@dataclass
class RecordLiteral(Expr):
    fields: dict[str, Expr]
    line: int
    col: int    
    
 