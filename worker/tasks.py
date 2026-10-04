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
from flowscript.environment import FlowRuntimeError
from flowscript.parser import ParseError


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


@celery_app.task(name="run_script_execution")
def run_script_execution_task(execution_id: str):

    db = SessionLocal()

    try:
        # --------------------------------
        # 1. Find execution
        # --------------------------------

        execution = (
            db.query(Execution)
            .filter(
                Execution.id == UUID(execution_id)
            )
            .first()
        )

        if execution is None:
            return

        # --------------------------------
        # 2. Find associated script
        # --------------------------------

        script = (
            db.query(Script)
            .filter(
                Script.id == execution.script_id
            )
            .first()
        )

        if script is None:
            execution.status = ExecutionStatus.FAILED
            execution.error_message = "Script not found"
            execution.finished_at = datetime.now(timezone.utc)

            db.commit()

            return

        # --------------------------------
        # 3. Mark execution as RUNNING
        # --------------------------------

        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now(timezone.utc)

        db.commit()

        # --------------------------------
        # 4. Create worker-side log callback
        # --------------------------------

        log_callback = make_log_callback(
            db,
            execution.id
        )

        # --------------------------------
        # 5. Run FlowScript
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
        # 6. Execution succeeded
        # --------------------------------

        execution.status = ExecutionStatus.SUCCEEDED
        execution.finished_at = datetime.now(timezone.utc)

        db.commit()

    except ParseError as error:

        # --------------------------------
        # 7. FlowScript syntax error
        # --------------------------------

        execution.status = ExecutionStatus.FAILED
        execution.error_message = error.message
        execution.error_line = error.line
        execution.error_col = error.col
        execution.finished_at = datetime.now(timezone.utc)

        db.commit()

    except FlowRuntimeError as error:

        # --------------------------------
        # 8. FlowScript runtime error
        # --------------------------------

        execution.status = ExecutionStatus.FAILED
        execution.error_message = error.message
        execution.error_line = error.line
        execution.error_col = error.col
        execution.finished_at = datetime.now(timezone.utc)

        db.commit()

    except Exception as error:

        # --------------------------------
        # 9. Unexpected worker error
        # --------------------------------

        execution.status = ExecutionStatus.FAILED
        execution.error_message = str(error)
        execution.finished_at = datetime.now(timezone.utc)

        db.commit()

        raise

    finally:

        # --------------------------------
        # 10. Close worker DB session
        # --------------------------------

        db.close()