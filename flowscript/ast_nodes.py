from dataclasses import dataclass
from typing import Optional, Union

#---------base nodes---------------------------------------
class Expr:
    """Base class for all expression AST nodes."""
    pass

class Stmt:
    """Base class for all statement AST nodes."""
    pass

#---------------expression nodes----------------------------
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
    base: Expr
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
    
 #---------------helper nodes-----------------------------

@dataclass
class Parameter:
    name: str
    type_annotation: Optional[str]

#-------------------statement nodes-----------------------

@dataclass
class LetStmt(Stmt):
    name: str
    type_annotation: Optional[str]
    value: Expr
    line: int
    col: int


@dataclass
class AssignStmt(Stmt):
    target: Expr
    value: Expr
    line: int
    col: int


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: list[Stmt]
    else_branch: Optional[list[Stmt]]
    line: int
    col: int


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: list[Stmt]
    line: int
    col: int


@dataclass
class ForStmt(Stmt):
    variable: str
    iterable: Expr
    body: list[Stmt]
    line: int
    col: int


@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr]
    line: int
    col: int


@dataclass
class ExprStmt(Stmt):
    expression: Expr
    line: int
    col: int

#--------------- Flow Definition Nodes-----------------------

@dataclass
class TaskDef:
    name: str
    params: list[Parameter]
    body: list[Stmt]
    line: int
    col: int


@dataclass
class OnFailClause:
    body: list[Stmt]
    line: int
    col: int


@dataclass
class StepDef:
    label: str
    body: list[Stmt]
    on_fail: Optional[OnFailClause]
    line: int
    col: int


@dataclass
class FlowDef:
    name: str
    body: list[Union[TaskDef, StepDef, Stmt]]
    line: int
    col: int


@dataclass
class Program:
    flows: list[FlowDef]    