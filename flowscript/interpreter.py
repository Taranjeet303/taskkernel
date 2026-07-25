from .ast_nodes import (
    NumberLiteral, StringLiteral, BooleanLiteral, Identifier,
    BinaryOp, UnaryOp, Call, MemberAccess, ListLiteral, RecordLiteral,
)
from .environment import Environment, FlowRuntimeError


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
        left = self.evaluate(node.left, env)
        right = self.evaluate(node.right, env)
        op = node.operator

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


        if op == "and":
            return bool(left) and bool(right)


        if op == "or":
            return bool(left) or bool(right)

        raise FlowRuntimeError(f"Unknown operator '{op}'", node.line, node.col)

    def eval_UnaryOp(self, node: UnaryOp, env: Environment):
        # YOUR TASK:
        # operand = self.evaluate(node.operand, env)
        # if node.operator == "not": return boolean negation
        # if node.operator == "-": return numeric negation (raise error if not a number)
        pass

    # ---------- YOUR TASK: implement these ----------

    def eval_MemberAccess(self, node: MemberAccess, env: Environment):
        """
        Evaluate node.base to get a value (should be a dict, since Records
        are represented as Python dicts — see eval_RecordLiteral below).
        Look up node.member in that dict.
        Raise FlowRuntimeError if the base isn't a dict, or the member doesn't exist.
        """
        pass

    def eval_ListLiteral(self, node: ListLiteral, env: Environment):
        """Evaluate every element, return a Python list."""
        pass

    def eval_RecordLiteral(self, node: RecordLiteral, env: Environment):
        """
        Evaluate every value in node.fields, return a Python dict
        mapping the same string keys to the evaluated values.
        """
        pass

    def eval_Call(self, node: Call, env: Environment):
        """
        Leave this as a stub for now — raise NotImplementedError.
        Function/task calls and built-ins are Day 5's job, since they need
        statement execution (task bodies are statement lists) to exist first.
        """
        raise NotImplementedError("Call evaluation comes in Day 5")