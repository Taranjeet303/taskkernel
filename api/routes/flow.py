from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from flowscript import lexer, parser, interpreter
from flowscript.environment import FlowRuntimeError
from flowscript.parser import ParseError

from api.schemas import RunRequest
from db.session import get_db
from models.models import Script, Execution, ExecutionStatus


router = APIRouter()


@router.post("/run")
def run_flow(
    request: RunRequest,
    db: Session = Depends(get_db)
):
    # 1. Create a Script row
    script = Script(
        name="Ad-hoc execution",
        source=request.source
    )

    db.add(script)
    db.commit()
    db.refresh(script)

    # 2. Create an Execution row with PENDING status
    execution = Execution(
        script_id=script.id,
        status=ExecutionStatus.SUBMITTED
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    # 3. Change status to RUNNING
    execution.status = ExecutionStatus.RUNNING
    db.commit()

    try:
        # 4. Lex the source code
        tokens = lexer.Lexer(request.source).tokenize()

        # 5. Parse tokens into AST/program
        program = parser.Parser(tokens).parse()

        # 6. Create interpreter
        runtime = interpreter.Interpreter()

        # 7. Execute the program
        runtime.run(program)

        # 8. Execution succeeded
        execution.status = ExecutionStatus.SUCCEEDED
        db.commit()

        return {
            "status": "success",
            "execution_id": str(execution.id)
        }

    except ParseError as error:
        execution.status = ExecutionStatus.FAILED
        execution.error_message = error.message
        execution.error_line = error.line
        execution.error_col = error.col
        db.commit()

        return JSONResponse(
            status_code=400,
            content={
                "error": "syntax_error",
                "message": error.message,
                "line": error.line,
                "col": error.col,
                "execution_id": str(execution.id)
            }
        )

    except FlowRuntimeError as error:
        execution.status = ExecutionStatus.FAILED
        execution.error_message = error.message
        execution.error_line = error.line
        execution.error_col = error.col
        db.commit()

        return JSONResponse(
            status_code=422,
            content={
                "error": "runtime_error",
                "message": error.message,
                "line": error.line,
                "col": error.col,
                "execution_id": str(execution.id)
            }
        )