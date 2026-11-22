from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas import ExecutionResponse, ExecutionLogResponse
from db.session import get_db
from models.models import Script, Execution, ExecutionStatus, ExecutionLog
from datetime import datetime, timezone

from worker.tasks import run_script_execution_task
router = APIRouter()

# Maximum time an execution can remain RUNNING before being considered stuck.
EXECUTION_TIMEOUT_SECONDS = 360


def cleanup_stuck_execution(db: Session, execution: Execution):
    if execution.status != ExecutionStatus.RUNNING:
        return

    if execution.started_at is None:
        return

    now = datetime.now(timezone.utc)
    elapsed = now - execution.started_at

    if elapsed.total_seconds() <= EXECUTION_TIMEOUT_SECONDS:
        return

    execution.status = ExecutionStatus.FAILED
    execution.error_type = "WORKER_LOST"
    execution.exception_type = None
    execution.error_message = (
        "Worker appears to have been lost while executing this script."
    )
    execution.finished_at = now

    db.commit()
    db.refresh(execution)

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

    if script is None:
        raise HTTPException(
            status_code=404,
            detail="Script not found"
        )

    # 2. Create execution record
    execution = Execution(
        script_id=script.id,
        status=ExecutionStatus.SUBMITTED
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    # 3. Send execution to Celery
    run_script_execution_task.delay(
        str(execution.id)
    )

    # 4. Return immediately
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
    cleanup_stuck_execution(db, execution)

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
    for execution in executions:
        cleanup_stuck_execution(db, execution)

    return executions    

@router.get(
    "/executions/{execution_id}/logs",
    response_model=list[ExecutionLogResponse]
)
def get_execution_logs(
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

    logs = (
        db.query(ExecutionLog)
        .filter(ExecutionLog.execution_id == execution_id)
        .order_by(ExecutionLog.sequence.asc())
        .all()
    )

    return logs