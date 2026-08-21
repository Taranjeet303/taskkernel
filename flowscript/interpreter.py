from .ast_nodes import (
    NumberLiteral, StringLiteral, BooleanLiteral, Identifier,
    BinaryOp, UnaryOp, Call, MemberAccess, ListLiteral, RecordLiteral,
)
from .environment import Environment, FlowRuntimeError

class ReturnSignal(Exception):
    """Not an error — used to unwind the call stack back to a task call
    when a `return` statement executes, carrying the returned value."""
    def __init__(self, value):
        self.value = value


class Interpreter:
    def __init__(self):
        self.globals = Environment()

    def is_number(self, value) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)    

    def evaluate(self, node, env: Environment):
        """Dispatch to the correct eval_* method based on node type."""
        method_name = f"eval_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise FlowRuntimeError(
                f"No evaluator for node type {type(node).__name__}",
                getattr(node, "line", 0),
                getattr(node, "col", 0),
            )
        return method(node, env)

    def execute(self, stmt, env: Environment):
        """Dispatch to the correct exec_* method based on statement type."""
        method_name = f"exec_{type(stmt).__name__}"
        method = getattr(self, method_name, None)

        if method is None:
            raise FlowRuntimeError(
                f"No executor for statement type {type(stmt).__name__}",
                getattr(stmt, "line", 0),
                getattr(stmt, "col", 0),
            )

        method(stmt, env)

    def execute_block(self, statements: list, env: Environment):
        """Execute a list of statements in a given environment."""
        for stmt in statements:
            self.execute(stmt, env)    

    def exec_LetStmt(self, stmt, env: Environment):
        value = self.evaluate(stmt.value, env)
        env.define(stmt.name, value)        
    # ---------- literals ----------

    def eval_NumberLiteral(self, node: NumberLiteral, env: Environment):
        return node.value

    def eval_StringLiteral(self, node: StringLiteral, env: Environment):
        return node.value

    def eval_BooleanLiteral(self, node: BooleanLiteral, env: Environment):
        return node.value

    def eval_Identifier(self, node: Identifier, env: Environment):
        return env.get(node.name, node.line, node.col)

    # ---------- binary / unary ----------

    def eval_BinaryOp(self, node: BinaryOp, env: Environment):
        
        op = node.operator

        if op == "and":
            left = self.evaluate(node.left, env)

            if not bool(left):
                return False

            right = self.evaluate(node.right, env)
            return bool(right)

        if op == "or":
            left = self.evaluate(node.left, env)

            if bool(left):
                return True

            right = self.evaluate(node.right, env)
            return bool(right)

        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)

        if op == "+":
            if self.is_number(left) and self.is_number(right):
                return left + right

            if isinstance(left, str) and isinstance(right, str):
                return left + right

            raise FlowRuntimeError(
                f"Cannot apply '+' to {type(left).__name__} and {type(right).__name__}",
                node.line,
                node.col,
            )

        if op == "-":
            if self.is_number(left) and self.is_number(right):
                return left - right

            raise FlowRuntimeError(
                f"Cannot apply '-' to {type(left).__name__} and {type(right).__name__}",
                node.line,
                node.col,
            )

        if op == "*":
            if self.is_number(left) and self.is_number(right):
                return left * right


            raise FlowRuntimeError(
                f"Cannot apply '*' to {type(left).__name__} and {type(right).__name__}",
                node.line,
                node.col,
            )

        if op == "/":
            if not self.is_number(left) or not self.is_number(right):
                raise FlowRuntimeError(
                    f"Cannot apply '/' to {type(left).__name__} and {type(right).__name__}",
                    node.line,
                    node.col,
                )

            if right == 0:
                raise FlowRuntimeError(
                    "Division by zero.",
                    node.line,
                    node.col,
                )

            return left / right

        if op == "==":
            return left == right


        if op == "!=":
            return left != right


        if op == "<":
            if self.is_number(left) and self.is_number(right):
                return left < right

            raise FlowRuntimeError(
                f"Cannot apply '<' to {type(left).__name__} and {type(right).__name__}",
                node.line,
                node.col,
            )


        if op == ">":
            if self.is_number(left) and self.is_number(right):
                return left > right

            raise FlowRuntimeError(
                f"Cannot apply '>' to {type(left).__name__} and {type(right).__name__}",
                node.line,
                node.col,
            )


        if op == "<=":
            if self.is_number(left) and self.is_number(right):
                return left <= right

            raise FlowRuntimeError(
                f"Cannot apply '<=' to {type(left).__name__} and {type(right).__name__}",
                node.line,
                node.col,
            )


        if op == ">=":
            if self.is_number(left) and self.is_number(right):
                return left >= right

            raise FlowRuntimeError(
                f"Cannot apply '>=' to {type(left).__name__} and {type(right).__name__}",
                node.line,
                node.col,
            )


        

        raise FlowRuntimeError(f"Unknown operator '{op}'", node.line, node.col)

    def eval_UnaryOp(self, node: UnaryOp, env: Environment):
        operand = self.evaluate(node.operand, env)

        if node.operator == "not":
            return not bool(operand)

        if node.operator == "-":
            if self.is_number(operand):
                return -operand

            raise FlowRuntimeError(
                f"Cannot apply unary '-' to {type(operand).__name__}",
                node.line,
                node.col,
            )

        raise FlowRuntimeError(
            f"Unknown unary operator '{node.operator}'",
            node.line,
            node.col,
    )

    def eval_MemberAccess(self, node: MemberAccess, env: Environment):
        base = self.evaluate(node.base, env)

        if not isinstance(base, dict):
            raise FlowRuntimeError(
                "Member access is only supported on records.",
                node.line,
                node.col,
            )

        if node.member not in base:
            raise FlowRuntimeError(
                f"Record has no member '{node.member}'",
                node.line,
                node.col,
            )

        return base[node.member]

    def eval_ListLiteral(self, node: ListLiteral, env: Environment):
        result = []

        for element in node.elements:
            result.append(self.evaluate(element, env))

        return result

    def eval_RecordLiteral(self, node: RecordLiteral, env: Environment):
        result = {}

        for key, value in node.fields.items():
            result[key] = self.evaluate(value, env)

        return result

    def eval_Call(self, node: Call, env: Environment):
        """
        Leave this as a stub for now — raise NotImplementedError.
        Function/task calls and built-ins are Day 5's job, since they need
        statement execution (task bodies are statement lists) to exist first.
        """
        raise NotImplementedError("Call evaluation comes in Day 5")