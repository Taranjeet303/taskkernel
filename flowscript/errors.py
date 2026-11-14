class FlowRuntimeError(Exception):
    def __init__(self, message: str, line: int, col: int):
        self.message = message
        self.line = line
        self.col = col
        super().__init__(f"Runtime error at line {line}, col {col}: {message}")

class RetrySignal(Exception):
    """Signals the step executor to retry a failed step."""

    def __init__(self, attempts):
        self.attempts = attempts