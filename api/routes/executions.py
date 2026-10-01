from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas import ExecutionResponse
from db.session import get_db
from models.models import Script, Execution, ExecutionStatus

from flowscript import lexer, parser, interpreter
from flowscript.environment import FlowRuntimeError
from flowscript.parser import ParseError


router = APIRouter()

@router.post("/scripts/{script_id}/run", response_model=ExecutionResponse)
def run_script(
    script_id: UUID,
    db: Session = Depends(get_db)
):
    # 1. Find the saved script
    script = (
        db.query(Script)
        .filter(Script.id == script_id)
        .first()
    )

    # 2. Script doesn't exist
    if script is None:
        raise HTTPException(
            status_code=404,
            detail="Script not found"
        )

    # 3. Create an execution record
    execution = Execution(
        script_id=script.id,
        status=ExecutionStatus.SUBMITTED
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    # 4. Mark execution as running
    execution.status = ExecutionStatus.RUNNING
    execution.started_at = datetime.now(timezone.utc)

    db.commit()

    try:
        # 5. Run the saved FlowScript
        tokens = lexer.Lexer(script.source).tokenize()
        program = parser.Parser(tokens).parse()

        runtime = interpreter.Interpreter()
        runtime.run(program)

        # 6. Execution succeeded
        execution.status = ExecutionStatus.SUCCEEDED
        execution.finished_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(execution)

        return execution

    except ParseError as error:
        # 7. Syntax error
        execution.status = ExecutionStatus.FAILED
        execution.error_message = error.message
        execution.error_line = error.line
        execution.error_col = error.col
        execution.finished_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(execution)

        return execution

    except FlowRuntimeError as error:
        # 8. Runtime error
        execution.status = ExecutionStatus.FAILED
        execution.error_message = error.message
        execution.error_line = error.line
        execution.error_col = error.col
        execution.finished_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(execution)

        return execution

@router.get(
    "/executions/{execution_id}",
    response_model=ExecutionResponse
)
def get_execution(
    execution_id: UUID,
    db: Session = Depends(get_db)
):
    execution = (
        db.query(Execution)
        .filter(Execution.id == execution_id)
        .first()
    )

    if execution is None:
        raise HTTPException(
            status_code=404,
            detail="Execution not found"
        )

    return execution


@router.get(
    "/executions",
    response_model=list[ExecutionResponse]
)
def list_executions(
    db: Session = Depends(get_db)
):
    executions = (
        db.query(Execution)
        .order_by(Execution.started_at.desc())
        .all()
    )

    return executions    