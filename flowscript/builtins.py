import httpx
import time
from .errors import FlowRuntimeError

import os
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    inspect,
    text,
    and_,
)

from sqlalchemy.exc import SQLAlchemyError, NoSuchTableError

# -------------------------
# Workflow Database Connection
# -------------------------

class DatabaseConnectionManager:

    def __init__(self):
        self._engine = None

    def get_engine(self):

        if self._engine is not None:
            return self._engine

        database_url = os.getenv("WORKFLOW_DB_URL")

        if not database_url:
            raise RuntimeError(
                "Workflow database is not configured. "
                "Set WORKFLOW_DB_URL in your .env file."
            )

        self._engine = create_engine(
            database_url,
            pool_pre_ping=True,
        )

        return self._engine

    def close(self):

        if self._engine is not None:
            self._engine.dispose()
            self._engine = None


database_manager = DatabaseConnectionManager()

# -------------------------
# HTTP Operations
# -------------------------


def builtin_http_get(args, interpreter, line=0, col=0):
    if len(args) != 1:
        raise FlowRuntimeError(
            "http_get() expects exactly one argument: url",
            line,
            col,
        )

    url = args[0]

    if not isinstance(url, str) or not url.strip():
        raise FlowRuntimeError(
            "http_get() url must be a non-empty string",
            line,
            col,
        )

    start_time = time.perf_counter()

    try:
        response = httpx.get(url, timeout=10)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        try:
            body = response.json()
        except ValueError:
            body = response.text

        result = {
            "status": response.status_code,
            "body": body,
            "url": str(response.url),
            "method": "GET",
        }

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "http_get",
            "url": str(response.url),
            "status": response.status_code,
            "duration_ms": duration_ms,
            "line": line,
            "col": col,
            "result_summary": {
                "status": response.status_code,
                "body_type": (
                    "json" if isinstance(body, (dict, list))
                    else "text"
                ),
            },
        })

        return result

    except httpx.RequestError as e:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "http_get",
            "url": url,
            "status": "error",
            "duration_ms": duration_ms,
            "line": line,
            "col": col,
            "message": str(e),
        })

        raise FlowRuntimeError(
            f"HTTP request failed: {e}",
            line,
            col,
        ) from e



def builtin_http_post(args, interpreter, line=0, col=0):
    if len(args) != 2:
        raise FlowRuntimeError(
            "http_post() expects two arguments: url, body",
            line,
            col,
        )

    url, body = args

    if not isinstance(url, str) or not url.strip():
        raise FlowRuntimeError(
            "http_post() url must be a non-empty string",
            line,
            col,
        )

    start_time = time.perf_counter()

    try:
        response = httpx.post(url, json=body, timeout=10)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text

        result = {
            "status": response.status_code,
            "body": response_body,
            "url": str(response.url),
            "method": "POST",
        }

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "http_post",
            "url": str(response.url),
            "status": response.status_code,
            "duration_ms": duration_ms,
            "line": line,
            "col": col,
            "result_summary": {
                "status": response.status_code,
                "body_type": (
                    "json"
                    if isinstance(response_body, (dict, list))
                    else "text"
                ),
            },
        })

        return result

    except httpx.RequestError as e:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "http_post",
            "url": url,
            "status": "error",
            "duration_ms": duration_ms,
            "line": line,
            "col": col,
            "message": str(e),
        })

        raise FlowRuntimeError(
            f"HTTP POST request failed: {e}",
            line,
            col,
        ) from e


def builtin_http_put(args, interpreter, line=0, col=0):
    if len(args) != 2:
        raise FlowRuntimeError(
            "http_put() expects two arguments: url, body",
            line,
            col,
        )

    url, body = args

    if not isinstance(url, str) or not url.strip():
        raise FlowRuntimeError(
            "http_put() url must be a non-empty string",
            line,
            col,
        )

    start_time = time.perf_counter()

    try:
        response = httpx.put(url, json=body, timeout=10)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text

        result = {
            "status": response.status_code,
            "body": response_body,
            "url": str(response.url),
            "method": "PUT",
        }

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "http_put",
            "url": str(response.url),
            "status": response.status_code,
            "duration_ms": duration_ms,
            "line": line,
            "col": col,
            "result_summary": {
                "status": response.status_code,
                "body_type": (
                    "json"
                    if isinstance(response_body, (dict, list))
                    else "text"
                ),
            },
        })

        return result

    except httpx.RequestError as e:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "http_put",
            "url": url,
            "status": "error",
            "duration_ms": duration_ms,
            "line": line,
            "col": col,
            "message": str(e),
        })

        raise FlowRuntimeError(
            f"HTTP PUT request failed: {e}",
            line,
            col,
        ) from e


def builtin_http_patch(args, interpreter, line=0, col=0):
    if len(args) != 2:
        raise FlowRuntimeError(
            "http_patch() expects two arguments: url, body",
            line,
            col,
        )

    url, body = args

    if not isinstance(url, str) or not url.strip():
        raise FlowRuntimeError(
            "http_patch() url must be a non-empty string",
            line,
            col,
        )

    start_time = time.perf_counter()

    try:
        response = httpx.patch(url, json=body, timeout=10)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text

        result = {
            "status": response.status_code,
            "body": response_body,
            "url": str(response.url),
            "method": "PATCH",
        }

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "http_patch",
            "url": str(response.url),
            "status": response.status_code,
            "duration_ms": duration_ms,
            "line": line,
            "col": col,
            "result_summary": {
                "status": response.status_code,
                "body_type": (
                    "json"
                    if isinstance(response_body, (dict, list))
                    else "text"
                ),
            },
        })

        return result

    except httpx.RequestError as e:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "http_patch",
            "url": url,
            "status": "error",
            "duration_ms": duration_ms,
            "line": line,
            "col": col,
            "message": str(e),
        })

        raise FlowRuntimeError(
            f"HTTP PATCH request failed: {e}",
            line,
            col,
        ) from e


def builtin_http_delete(args, interpreter, line=0, col=0):
    if len(args) != 1:
        raise FlowRuntimeError(
            "http_delete() expects exactly one argument: url",
            line,
            col,
        )

    url = args[0]

    if not isinstance(url, str) or not url.strip():
        raise FlowRuntimeError(
            "http_delete() url must be a non-empty string",
            line,
            col,
        )

    start_time = time.perf_counter()

    try:
        response = httpx.delete(url, timeout=10)

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        try:
            response_body = response.json()
        except ValueError:
            response_body = response.text

        result = {
            "status": response.status_code,
            "body": response_body,
            "url": str(response.url),
            "method": "DELETE",
        }

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "http_delete",
            "url": str(response.url),
            "status": response.status_code,
            "duration_ms": duration_ms,
            "line": line,
            "col": col,
            "result_summary": {
                "status": response.status_code,
                "body_type": (
                    "json"
                    if isinstance(response_body, (dict, list))
                    else "text"
                ),
            },
        })

        return result

    except httpx.RequestError as e:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "http_delete",
            "url": url,
            "status": "error",
            "duration_ms": duration_ms,
            "line": line,
            "col": col,
            "message": str(e),
        })

        raise FlowRuntimeError(
            f"HTTP DELETE request failed: {e}",
            line,
            col,
        ) from e


# -------------------------
# Database Helper Functions
# -------------------------

def get_workflow_connection():
    engine = database_manager.get_engine()
    return engine.connect()


def get_workflow_table(connection, table_name):

    if not isinstance(table_name, str) or not table_name.strip():
        raise ValueError("Table name must be a non-empty string.")

    metadata = MetaData()

    table = Table(
        table_name,
        metadata,
        autoload_with=connection,
    )

    return table


def validate_record(record):

    if not isinstance(record, dict) or not record:
        raise ValueError("Record must be a non-empty dictionary.")

    return record


def validate_conditions(conditions):

    if not isinstance(conditions, dict) or not conditions:
        raise ValueError("Conditions must be a non-empty dictionary.")

    return conditions    

# -------------------------
# Database Operations
# -------------------------

def builtin_db_query(args, interpreter):

    # Step 1: Validate arguments
    if len(args) != 1:
        raise FlowRuntimeError(
            "db_query() expects exactly one argument: query"
        )

    query = args[0]

    if not isinstance(query, str) or not query.strip():
        raise FlowRuntimeError(
            "db_query() query must be a non-empty string"
        )

    # Step 2: Start measuring execution time
    start_time = time.perf_counter()

    try:

        # Step 3: Get the workflow database connection
        with get_workflow_connection() as connection:

            # Step 4: Execute the SQL query
            result = connection.execute(text(query))

            # Step 5: Convert database rows into dictionaries
            if not result.returns_rows:
                raise FlowRuntimeError(
                    "db_query() expects a query that returns rows."
                )

            rows = [
                dict(row._mapping)
                for row in result.fetchall()
            ]

        # Step 6: Calculate execution time
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        # Step 7: Record successful execution
        interpreter.emit_log({
            "type": "builtin_call",
            "name": "db_query",
            "status": "success",
            "row_count": len(rows),
            "duration_ms": duration_ms,
        })

        # Step 8: Return the result to FlowScript
        return {
            "success": True,
            "query": query,
            "rows": rows,
            "row_count": len(rows),
        }

    except SQLAlchemyError as e:

        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        interpreter.emit_log({
            "type": "builtin_call",
            "name": "db_query",
            "status": "error",
            "duration_ms": duration_ms,
            "message": str(e),
        })

        raise FlowRuntimeError(
            f"Database query failed: {e}"
        ) from e


def builtin_db_insert(args, interpreter):
    return {
        "success": True,
        "operation": "insert",
        "table": args[0],
        "record": args[1],
    }


def builtin_db_update(args, interpreter):
    return {
        "success": True,
        "operation": "update",
        "table": args[0],
        "record": args[1],
        "updates": args[2],
    }


def builtin_db_delete(args, interpreter):
    return {
        "success": True,
        "operation": "delete",
        "table": args[0],
        "condition": args[1],
    }


# -------------------------
# Event Operations
# -------------------------

def builtin_publish_event(args, interpreter):
    return {
        "success": True,
        "operation": "publish_event",
        "channel": args[0],
        "message": args[1],
    }


# -------------------------
# Notification Operations
# -------------------------

def builtin_notify(args, interpreter):
    return {
        "success": True,
        "operation": "notify",
        "message": args[0],
    }


# -------------------------
# Runtime Operations
# -------------------------

def builtin_log(args, interpreter):
    print(f"[LOG] {args[0]}")

    return {
        "success": True,
        "operation": "log",
        "message": args[0],
    }


def builtin_wait(args, interpreter):
    import time

    time.sleep(args[0])

    return {
        "success": True,
        "operation": "wait",
        "seconds": args[0],
    }


def builtin_retry(args, interpreter):
    return {
        "success": True,
        "operation": "retry",
        "attempts": args[0],
    }

def builtin_print(arguments, interpreter):
    print(*arguments)
    return None

# -------------------------
# Built-in Function Registry
# -------------------------

BUILTINS = {
    # Output
    "print": builtin_print,
    # HTTP
    "http_get": builtin_http_get,
    "http_post": builtin_http_post,
    "http_put": builtin_http_put,
    "http_patch": builtin_http_patch,
    "http_delete": builtin_http_delete,

    # Database
    "db_query": builtin_db_query,
    "db_insert": builtin_db_insert,
    "db_update": builtin_db_update,
    "db_delete": builtin_db_delete,

    # Events
    "publish_event": builtin_publish_event,

    # Notifications
    "notify": builtin_notify,

    # Runtime
    "log": builtin_log,
    "wait": builtin_wait,
    "retry": builtin_retry,
}