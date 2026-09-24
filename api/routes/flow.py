from fastapi import APIRouter
from flowscript import lexer, parser, interpreter
from flowscript.environment import  FlowRuntimeError
from flowscript.parser import ParseError
from api.schemas import RunRequest
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post("/run")
def run_flow(request: RunRequest):
    try:
        # 1. lex the source code
        tokens= lexer.Lexer(request.source).tokenize()

        # 2. parse the tokens into AST/programs
        program= parser.Parser(tokens).parse()

        # 3. creating interpreter
        runtime= interpreter.Interpreter()

        # 4. execute the program
        runtime.run(program)

        # 5. Successful execution
        return {
            "status": "success"
        }

    except ParseError as error:
        return JSONResponse(
            status_code=400,
            content={
                "error": "syntax_error",
                "message": error.message,
                "line": error.line,
                "col": error.col
            }
        )
    except FlowRuntimeError as error:
        return JSONResponse(
            status_code=422,
            content={
                "error": "runtime_error",
                "message": error.message,
                "line": error.line,
                "col": error.col
            }
        )