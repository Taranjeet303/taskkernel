
class FlowScriptError(Exception):
    """Base class for errors caused by invalid FlowScript code."""

    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"FlowScript error at line {line}, col {col}: {message}")


class FlowRuntimeError(FlowScriptError):
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        Exception.__init__(
            self,
            f"Runtime error at line {line}, col {col}: {message}"
        )


class RetrySignal(Exception):
    """Signals the step executor to retry a failed step."""

    def __init__(self, attempts):
        self.attempts = attempts
