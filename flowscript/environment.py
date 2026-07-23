class FlowRuntimeError(Exception):
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"Runtime error at line {line}, col {col}: {message}")


class Environment:
    def __init__(self, parent: "Environment" = None):
        self.parent = parent
        self.values = {}

    def define(self, name: str, value):
        """Create a new variable in THIS scope (used by `let`)."""
        self.values[name] = value

    def get(self, name: str, line: int, col: int):
        """Look up a variable, checking parent scopes if not found locally."""
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name, line, col)
        raise FlowRuntimeError(f"Undefined variable '{name}'", line, col)

    def assign(self, name: str, value, line: int, col: int):
        """Update an EXISTING variable (used by assignment, not `let`)."""
        if name in self.values:
            self.values[name] = value
            return
        if self.parent is not None:
            self.parent.assign(name, value, line, col)
            return
        raise FlowRuntimeError(f"Undefined variable '{name}'", line, col)