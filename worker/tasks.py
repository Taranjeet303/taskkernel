from datetime import datetime, timezone
from uuid import UUID

from worker.celery_app import celery_app

from db.session import SessionLocal
from models.models import (
    Script,
    Execution,
    ExecutionStatus,
    ExecutionLog,
)

from flowscript import lexer, parser, interpreter
from flowscript.errors import FlowScriptError

import logging

logger = logging.getLogger(__name__)

def make_log_callback(
    db,
    execution_id: UUID
):
    sequence = 0

    def callback(event: dict):
        nonlocal sequence

        sequence += 1

        log_row = ExecutionLog(
            execution_id=execution_id,

            step=event.get("step", ""),
            event_type=event.get("type", "step"),
            name=event.get("name"),

            message=event.get("message", ""),
            status=event.get("status", "success"),

            line=event.get("line"),
            col=event.get("col"),

            args=event.get("args"),
            result_summary=event.get("result_summary"),

            duration_ms=event.get("duration_ms"),

            sequence=sequence,
        )

        db.add(log_row)
        db.commit()

    return callback

def mark_execution_failed(
    db,
    execution_uuid: UUID,
    error_type: str,
    error_message: str,
    exception_type: str | None = None,
    error_line: int | None = None,
    error_col: int | None = None,
    status: ExecutionStatus = ExecutionStatus.FAILED,
):
    try:
        # Discard any incomplete transaction.
        db.rollback()

        # Fetch a fresh execution record.
        execution = (
            db.query(Execution)
            .filter(Execution.id == execution_uuid)
            .first()
        )

        if execution is None:
            logger.error(
                "Cannot record failure: execution %s was not found.",
                execution_uuid,
            )
            return

        execution.status = status
        execution.error_type = error_type
        execution.error_message = error_message
        execution.exception_type = exception_type
        execution.error_line = error_line
        execution.error_col = error_col
        execution.finished_at = datetime.now(timezone.utc)

        db.commit()

    except Exception:
        db.rollback()
        logger.exception(
            "Failed to persist failure status for execution %s",
            execution_uuid,
        )
        raise


@celery_app.task(name="run_script_execution",  acks_late=True)
def run_script_execution_task(execution_id: str):

    db = SessionLocal()
    execution_uuid = None

    try:
        # --------------------------------
        # 1. Validate execution ID
        # --------------------------------

        execution_uuid = UUID(execution_id)

        # --------------------------------
        # 2. Find execution
        # --------------------------------

        execution = (
            db.query(Execution)
            .filter(Execution.id == execution_uuid)
            .first()
        )

        if execution is None:
            logger.warning(
                "Execution %s was not found.",
                execution_id,
            )
            return

        # --------------------------------
        # 3. Find associated script
        # --------------------------------

        script = (
            db.query(Script)
            .filter(Script.id == execution.script_id)
            .first()
        )

        if script is None:
            mark_execution_failed(
                db=db,
                execution_uuid=execution_uuid,
                error_type="SYSTEM_ERROR",
                error_message="Associated script was not found.",
                exception_type=None,
            )
            return

        # --------------------------------
        # 4. Atomically claim execution
        # --------------------------------

        claimed = (
            db.query(Execution)
            .filter(
                Execution.id == execution_uuid,
                Execution.status == ExecutionStatus.SUBMITTED,
            )
            .update(
                {
                    Execution.status: ExecutionStatus.RUNNING,
                    Execution.started_at: datetime.now(timezone.utc),
                    Execution.finished_at: None,
                    Execution.error_type: None,
                    Execution.error_message: None,
                    Execution.exception_type: None,
                    Execution.error_line: None,
                    Execution.error_col: None,
                },
                synchronize_session=False,
            )
        )

        db.commit()

        # If this worker did not claim the execution, skip it.
        if claimed == 0:
            logger.info(
                "Execution %s is already claimed or completed. Skipping.",
                execution_id,
            )
            return

        # --------------------------------
        # 5. Create worker-side log callback
        # --------------------------------

        log_callback = make_log_callback(
            db,
            execution.id
        )

        # --------------------------------
        # 6. Run FlowScript
        # --------------------------------

        tokens = lexer.Lexer(
            script.source
        ).tokenize()

        program = parser.Parser(
            tokens
        ).parse()

        runtime = interpreter.Interpreter(
            log_callback=log_callback
        )

        runtime.run(program)

        # --------------------------------
        # 7. Execution succeeded
        # --------------------------------

        execution.status = ExecutionStatus.SUCCEEDED
        execution.finished_at = datetime.now(timezone.utc)

        # Ensure successful executions have no error information.
        execution.error_type = None
        execution.error_message = None
        execution.exception_type = None
        execution.error_line = None
        execution.error_col = None

        db.commit()

    # --------------------------------
    # 8. FlowScript errors
    # --------------------------------

    except FlowScriptError as error:

        mark_execution_failed(
            db=db,
            execution_uuid=execution_uuid,
            error_type="SCRIPT_ERROR",
            error_message=error.message,
            exception_type=type(error).__name__,
            error_line=error.line,
            error_col=error.col,
        )

        # Expected script failure.
        # Do not re-raise or trigger a Celery retry.

    # --------------------------------
    # 9. Unexpected worker errors
    # --------------------------------

    except Exception as error:

        logger.exception(
            "Unexpected error while executing script. Execution ID: %s",
            execution_id,
        )

        if execution_uuid is not None:
            mark_execution_failed(
                db=db,
                execution_uuid=execution_uuid,
                error_type="SYSTEM_ERROR",
                error_message="An internal error occurred during execution.",
                exception_type=type(error).__name__,
            )

        # Keep unexpected failures visible to Celery.
        raise

    finally:

        # --------------------------------
        # 10. Close worker DB session
        # --------------------------------

        db.close()