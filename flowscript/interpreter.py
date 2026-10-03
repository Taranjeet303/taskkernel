from .ast_nodes import (
    NumberLiteral, StringLiteral, BooleanLiteral, Identifier,
    BinaryOp, UnaryOp, Call, MemberAccess, ListLiteral, RecordLiteral,
    TaskDef, StepDef,
)
from .environment import Environment, FlowRuntimeError
from .builtins import BUILTINS
from typing import Callable
import time

class ReturnSignal(Exception):
    """Not an error — used to unwind the call stack back to a task call
    when a `return` statement executes, carrying the returned value."""
    def __init__(self, value):
        self.value = value


class Interpreter:
    
    def __init__(
        self,
        log_callback: Callable[[dict], None] | None = None
    ):
        self.globals = Environment()
        self.tasks = {}
        self.log_callback = log_callback
        self.current_step = None

    def emit_log(self, event: dict):
        
        if self.log_callback:
            self.log_callback(event)

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
  # ---------- collections / members ---------------

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
 # ------------------ calls ----------------
    def eval_Call(self, node: Call, env: Environment):
        name = node.callee.name

        # Check built-in functions first
        builtin = BUILTINS.get(name)

        if builtin is not None:
            arguments = []

            for argument in node.arguments:
                arguments.append(self.evaluate(argument, env))

            start_time = time.time()

            try:
                result = builtin(arguments, self)

                duration_ms = int(
                    (time.time() - start_time) * 1000
                )

                details = self.build_builtin_log_details(
                      name,
                      arguments,
                      result
                    )

                self.emit_log({
                    "type": "builtin_call",
                    "step": self.current_step or name,
                    "name": name,
                    "message": f"{name} completed",
                    "status": "success",
                    "line": node.line,
                    "col": node.col,
                    "args": details["args"],
                    "result_summary": details["result_summary"],
                    "duration_ms": duration_ms,
                    "timestamp": time.time(),
                })

                return result

            except FlowRuntimeError as error:

                duration_ms = int(
                    (time.time() - start_time) * 1000
                )

                details = self.build_builtin_log_details(
                    name,
                    arguments,
                    None
                )

                self.emit_log({
                    "type": "builtin_call",
                    "step": self.current_step or name,
                    "name": name,
                    "message": f"{name} failed: {error.message}",
                    "status": "failed",
                    "line": node.line,
                    "col": node.col,
                    "args": details["args"],
                    "result_summary": details["result_summary"],
                    "duration_ms": duration_ms,
                    "timestamp": time.time(),
                })

    
                raise

          # Check user-defined tasks
        task = self.tasks.get(name)

        if task is None:
            raise FlowRuntimeError(
                f"Undefined task '{name}'",
                node.line,
                node.col,
            )

        if len(node.arguments) != len(task.params):
            raise FlowRuntimeError(
                f"Task '{name}' expects {len(task.params)} argument(s), "
                f"but got {len(node.arguments)}",
                node.line,
                node.col,
            )

        arguments = []

        for argument in node.arguments:
            arguments.append(self.evaluate(argument, env))

        task_env = Environment(parent=self.globals)

        for parameter, argument in zip(task.params, arguments):
            task_env.define(parameter.name, argument)

        try:
            self.execute_block(task.body, task_env)
        except ReturnSignal as r:
            return r.value

        return None
#---------------- statement execution -----------------------------
   
    
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
        
                return method(stmt, env)
    
    def execute_block(self, statements: list, env: Environment):
            """Execute a list of statements in a given environment."""
            for stmt in statements:
                self.execute(stmt, env)    
    
    def exec_LetStmt(self, stmt, env: Environment):
            value = self.evaluate(stmt.value, env)
            env.define(stmt.name, value)       

    def exec_AssignStmt(self, stmt, env: Environment):
        # Evaluate the right-hand side, then update the existing variable.
        value = self.evaluate(stmt.value, env)
        env.assign(stmt.target.name, value, stmt.line, stmt.col)        

    def exec_IfStmt(self, stmt, env: Environment):
        condition = self.evaluate(stmt.condition, env)

        if bool(condition):
            child_env = Environment(parent=env)
            self.execute_block(stmt.then_branch, child_env)

        elif stmt.else_branch is not None:
            child_env = Environment(parent=env)
            self.execute_block(stmt.else_branch, child_env) 

    def exec_WhileStmt(self, stmt, env: Environment):
        while bool(self.evaluate(stmt.condition, env)):
            child_env = Environment(parent=env)
            self.execute_block(stmt.body, child_env)


    def exec_ForStmt(self, stmt, env: Environment):
        iterable = self.evaluate(stmt.iterable, env)

        if not isinstance(iterable, list):
            raise FlowRuntimeError(
                "For loop can only iterate over a list.",
                stmt.line,
                stmt.col,
            )

        for element in iterable:
            child_env = Environment(parent=env)
            child_env.define(stmt.variable, element)
            self.execute_block(stmt.body, child_env)

    def exec_ReturnStmt(self, stmt, env: Environment):
        value = self.evaluate(stmt.value, env) if stmt.value is not None else None
        raise ReturnSignal(value)        

    def exec_ExprStmt(self, stmt, env: Environment):
     self.evaluate(stmt.expression, env)

    def exec_Program(self, node, env: Environment):
        for flow in node.flows:
            return self.execute(flow, env)
        return None

    def exec_FlowDef(self, node, env: Environment):
        try:
            for item in node.body:
                if isinstance(item, TaskDef):
                    self.tasks[item.name] = item

                elif isinstance(item, StepDef):
                    try:
                        self.execute_block(item.body, env)

                    except FlowRuntimeError:
                        if item.on_fail is not None:
                            self.execute_block(item.on_fail.body, env)
                        else:
                            raise

                else:
                    self.execute(item, env)

        except ReturnSignal as r:
            return r.value

        return None
 #------------------- flow execution----------------     

    def run(self, program):
        """Execute all flows in the program in order."""

        if not program.flows:
            raise FlowRuntimeError(
                "No flow found in program.",
                0,
                0,
            )

        for flow in program.flows:

            # Tasks belong to the current flow.
            self.tasks.clear()

            # Register all tasks defined in this flow.
            for item in flow.body:
                if isinstance(item, TaskDef):
                    self.tasks[item.name] = item

            # Environment shared by the current flow.
            flow_env = Environment(parent=self.globals)

            # Execute everything in the flow in source order.
            for item in flow.body:

                # Task definitions are registered above,
                # but are not executed as statements.
                if isinstance(item, TaskDef):
                    continue

                # Steps get their own child scope.
                if isinstance(item, StepDef):

                    # Track which step is currently executing.
                    self.current_step = item.label

                    # Start timing the step.
                    start_time = time.time()

                    try:
                        step_env = Environment(parent=flow_env)

                        self.execute_block(
                            item.body,
                            step_env
                        )

                        # Step completed successfully.
                        duration_ms = int(
                            (time.time() - start_time) * 1000
                        )

                        self.emit_log({
                            "type": "step",
                            "step": item.label,
                            "message": "Step completed",
                            "status": "success",
                            "line": item.line,
                            "col": item.col,
                            "duration_ms": duration_ms,
                            "timestamp": time.time(),
})

                    except FlowRuntimeError as error:

                        # Step failed.
                        duration_ms = int(
                            (time.time() - start_time) * 1000
                        )

                        self.emit_log({
                            "type": "step",
                            "step": item.label,
                            "message": f"Step failed: {error.message}",
                            "status": "failed",
                            "line": item.line,
                            "col": item.col,
                            "duration_ms": duration_ms,
                            "timestamp": time.time(),
})

                        # Run on_fail if it exists.
                        if item.on_fail is not None:

                            fail_start_time = time.time()

                            fail_env = Environment(parent=flow_env)

                            self.execute_block(
                                item.on_fail.body,
                                fail_env
                            )

                            # on_fail completed successfully.
                            fail_duration_ms = int(
                                (time.time() - fail_start_time) * 1000
                            )

                            self.emit_log({
                                "type": "step",
                                "step": item.label,
                                "message": "on_fail handler completed",
                                "status": "recovered",
                                "line": item.line,
                                "col": item.col,
                                "duration_ms": fail_duration_ms,
                                "timestamp": time.time(),
})

                        else:
                            raise

                    finally:
                        # No step is currently active after this block.
                        self.current_step = None

                # Ordinary statements directly inside the flow.
                else:
                    self.execute(item, flow_env)

    def build_builtin_log_details(self, name, arguments, result):
        if name == "log":
            return {
                "args": {
                    "message": arguments[0] if arguments else ""
                },
                "result_summary": {
                    "operation": result.get("operation") if isinstance(result, dict) else None,
                    "success": result.get("success") if isinstance(result, dict) else None,
                },
            }

        if name == "print":
            return {
                "args": {
                    "values": arguments
                },
                "result_summary": None,
            }

        if name in {
            "http_get",
            "http_post",
            "http_put",
            "http_patch",
            "http_delete",
        }:
            return {
                "args": {
                    "url": arguments[0] if arguments else None,
                    "method": result.get("method") if isinstance(result, dict) else None,
                },
                "result_summary": {
                    "status": result.get("status") if isinstance(result, dict) else None,
                    "response_size": self.get_response_size(result),
                },
            }

        if name == "db_query":
            return {
                "args": {
                    "query": arguments[0] if arguments else None,
                },
                "result_summary": {
                    "success": result.get("success") if isinstance(result, dict) else None,
                    "row_count": len(result.get("rows", []))
                    if isinstance(result, dict)
                    else 0,
                },
            }

        if name == "db_insert":
            return {
                "args": {
                    "table": arguments[0] if arguments else None,
                    "record": arguments[1] if len(arguments) > 1 else None,
                },
                "result_summary": {
                    "success": result.get("success") if isinstance(result, dict) else None,
                    "operation": result.get("operation") if isinstance(result, dict) else None,
                },
            }

        if name == "db_update":
            return {
                "args": {
                    "table": arguments[0] if arguments else None,
                    "record": arguments[1] if len(arguments) > 1 else None,
                    "updates": arguments[2] if len(arguments) > 2 else None,
                },
                "result_summary": {
                    "success": result.get("success") if isinstance(result, dict) else None,
                    "operation": result.get("operation") if isinstance(result, dict) else None,
                },
            }

        if name == "db_delete":
            return {
                "args": {
                    "table": arguments[0] if arguments else None,
                    "condition": arguments[1] if len(arguments) > 1 else None,
                },
                "result_summary": {
                    "success": result.get("success") if isinstance(result, dict) else None,
                    "operation": result.get("operation") if isinstance(result, dict) else None,
                },
            }

        if name == "publish_event":
            return {
                "args": {
                    "channel": arguments[0] if arguments else None,
                    "message": arguments[1] if len(arguments) > 1 else None,
                },
                "result_summary": {
                    "success": result.get("success") if isinstance(result, dict) else None,
                    "operation": result.get("operation") if isinstance(result, dict) else None,
                },
            }

        if name == "notify":
            return {
                "args": {
                    "message": arguments[0] if arguments else None,
                },
                "result_summary": {
                    "success": result.get("success") if isinstance(result, dict) else None,
                    "operation": result.get("operation") if isinstance(result, dict) else None,
                },
            }

        if name == "wait":
            return {
                "args": {
                    "seconds": arguments[0] if arguments else None,
                },
                "result_summary": {
                    "success": result.get("success") if isinstance(result, dict) else None,
                    "seconds": result.get("seconds") if isinstance(result, dict) else None,
                },
            }

        if name == "retry":
            return {
                "args": {
                    "attempts": arguments[0] if arguments else None,
                },
                "result_summary": {
                    "success": result.get("success") if isinstance(result, dict) else None,
                    "attempts": result.get("attempts") if isinstance(result, dict) else None,
                },
            }

        return {
            "args": {
                "values": arguments
            },
            "result_summary": {
                "type": type(result).__name__
            }
        }

    def get_response_size(self, result):
        if not isinstance(result, dict):
            return None

        body = result.get("body")

        if body is None:
            return 0

        return len(str(body))

    def summarize_result(self, result):
        if result is None:
            return None

        if isinstance(result, dict):
            summary = {}

            for key in (
                "status_code",
                "status",
                "rows",
                "row_count",
                "affected_rows",
                "response_size",
            ):
                if key in result:
                    summary[key] = result[key]

            return summary or {
                "type": "dict"
            }

        if isinstance(result, list):
            return {
                "type": "list",
                "count": len(result),
            }

        return {
            "type": type(result).__name__
        }