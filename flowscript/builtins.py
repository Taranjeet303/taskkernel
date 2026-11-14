import httpx
import time
from .errors import FlowRuntimeError, RetrySignal
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

import json
import redis

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
# ------REDIS CONNECTION------------
redis_url = os.getenv("REDIS_URL")

if not redis_url:
    raise RuntimeError(
        "Redis is not configured. Set REDIS_URL in your .env file."
    )

redis_client = redis.Redis.from_url(redis_url)

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


def get_workflow_table(connection, table_name, line=0, col=0):
    if not isinstance(table_name, str) or not table_name.strip():
        raise FlowRuntimeError(
            "Table name must be a non-empty string.",
            line,
            col,
        )

    metadata = MetaData()

    try:
        return Table(
            table_name,
            metadata,
            autoload_with=connection,
        )
    except NoSuchTableError:
        raise FlowRuntimeError(
            f"Table '{table_name}' does not exist.",
            line,
            col,
        )


def validate_record(record):

    if not isinstance(record, dict) or not record:
        raise ValueError("Record must be a non-empty dictionary.")

    return record


def validate_conditions(conditions):

    if not isinstance(conditions, dict) or not conditions:
        raise ValueError("Conditions must be a non-empty dictionary.")

    return conditions    

def validate_table_fields(table, data, line, col):
    invalid_fields = set(data.keys()) - set(table.c.keys())

    if invalid_fields:
        raise FlowRuntimeError(
            f"Unknown column(s): {', '.join(invalid_fields)}",
            line,
            col,
        )

# -------------------------
# Database Operations
# -------------------------


def builtin_db_query(args, interpreter, line=0, col=0):

    if len(args) != 1:
        raise FlowRuntimeError(
            "db_query() expects exactly one argument: query",
            line,
            col,
        )

    query = args[0]

    if not isinstance(query, str) or not query.strip():
        raise FlowRuntimeError(
            "db_query() query must be a non-empty string",
            line,
            col,
        )

    start_time = time.perf_counter()

    try:
        with get_workflow_connection() as connection:
            result = connection.execute(text(query))

            if not result.returns_rows:
                raise FlowRuntimeError(
                    "db_query() expects a query that returns rows.",
                    line,
                    col,
                )

            rows = [
                dict(row._mapping)
                for row in result.fetchall()
            ]

        return {
            "success": True,
            "query": query,
            "rows": rows,
            "row_count": len(rows),
        }

    except SQLAlchemyError as e:
        raise FlowRuntimeError(
            f"Database query failed: {e}",
            line,
            col,
        ) from e


def builtin_db_insert(args, interpreter, line=0, col=0):

    if len(args) != 2:
        raise FlowRuntimeError(
            "db_insert() expects two arguments: table and record",
            line, col,
        )

    table_name, record = args

    try:
        validate_record(record)

        with database_manager.get_engine().begin() as connection:
            table = get_workflow_table(connection, table_name, line, col)
            validate_table_fields(table, record, line, col)

            result = connection.execute(
                table.insert().values(**record)
            )

            inserted_id = (
                list(result.inserted_primary_key)
                if result.inserted_primary_key
                else None
            )

        return {
            "success": True,
            "operation": "insert",
            "table": table_name,
            "record": record,
            "inserted_id": inserted_id,
            "row_count": 1,
        }

    except FlowRuntimeError:
        raise

    except (ValueError, SQLAlchemyError) as e:
        raise FlowRuntimeError(
            f"Database insert failed: {e}", line, col
        ) from e


def builtin_db_update(args, interpreter, line=0, col=0):

    if len(args) != 3:
        raise FlowRuntimeError(
            "db_update() expects three arguments: table, conditions, updates",
            line, col,
        )

    table_name, conditions, updates = args

    try:
        validate_conditions(conditions)
        validate_record(updates)

        with database_manager.get_engine().begin() as connection:
            table = get_workflow_table(connection, table_name, line, col)
            validate_table_fields(table, conditions, line, col)
            validate_table_fields(table, updates, line, col)

            where_clause = and_(
                *[
                    table.c[key] == value
                    for key, value in conditions.items()
                ]
            )

            result = connection.execute(
                table.update()
                .where(where_clause)
                .values(**updates)
            )

            affected_rows = result.rowcount

        return {
            "success": True,
            "operation": "update",
            "table": table_name,
            "conditions": conditions,
            "updates": updates,
            "row_count": affected_rows,
        }

    except FlowRuntimeError:
        raise

    except (ValueError, SQLAlchemyError) as e:
        raise FlowRuntimeError(
            f"Database update failed: {e}", line, col
        ) from e


def builtin_db_delete(args, interpreter, line=0, col=0):

    if len(args) != 2:
        raise FlowRuntimeError(
            "db_delete() expects two arguments: table and conditions",
            line, col,
        )

    table_name, conditions = args

    try:
        validate_conditions(conditions)

        with database_manager.get_engine().begin() as connection:
            table = get_workflow_table(connection, table_name, line, col)
            validate_table_fields(table, conditions, line, col)

            where_clause = and_(
                *[
                    table.c[key] == value
                    for key, value in conditions.items()
                ]
            )

            result = connection.execute(
                table.delete().where(where_clause)
            )

            affected_rows = result.rowcount

        return {
            "success": True,
            "operation": "delete",
            "table": table_name,
            "conditions": conditions,
            "row_count": affected_rows,
        }

    except FlowRuntimeError:
        raise

    except (ValueError, SQLAlchemyError) as e:
        raise FlowRuntimeError(
            f"Database delete failed: {e}", line, col
        ) from e



# -------------------------
# Event Operations
# -------------------------

def builtin_publish_event(args, interpreter, line=0, col=0):
    if len(args) != 2:
        raise FlowRuntimeError(
            "publish_event() expects 2 arguments: channel and message",
            line,
            col
        )

    channel, message = args

    if not isinstance(channel, str) or not channel.strip():
        raise FlowRuntimeError(
            "Event channel must be a non-empty string",
            line,
            col
        )

    try:
        serialized_message = json.dumps(message)
    except (TypeError, ValueError) as e:
        raise FlowRuntimeError(
            f"Event message must be JSON serializable: {e}",
            line,
            col
        )

    try:
        receiver_count = redis_client.publish(channel, serialized_message)
    except redis.RedisError as e:
        raise FlowRuntimeError(
            f"Failed to publish event: {e}",
            line,
            col
        )

    return {
        "success": True,
        "operation": "publish_event",
        "channel": channel,
        "receiver_count": receiver_count,
        "message": message
    }


# -------------------------
# Notification Operations
# -------------------------

def builtin_notify(args, interpreter, line=0, col=0):

    if len(args) != 1:
        raise FlowRuntimeError(
            "notify() expects exactly one argument: message",
            line,
            col,
        )

    message = args[0]

    if not isinstance(message, str) or not message.strip():
        raise FlowRuntimeError(
            "notify() message must be a non-empty string",
            line,
            col,
        )

    slack_url = os.getenv("SLACK_WEBHOOK_URL")
    discord_url = os.getenv("DISCORD_WEBHOOK_URL")

    destinations = {}

    if slack_url:
        destinations["slack"] = {
            "url": slack_url,
            "payload": {"text": message},
        }

    if discord_url:
        destinations["discord"] = {
            "url": discord_url,
            "payload": {"content": message},
        }

    if not destinations:
        raise FlowRuntimeError(
            "No notification webhook configured. "
            "Set SLACK_WEBHOOK_URL or DISCORD_WEBHOOK_URL.",
            line,
            col,
        )

    failed_providers = []

    for provider, config in destinations.items():

        try:
            response = httpx.post(
                config["url"],
                json=config["payload"],
                timeout=10,
            )

            response.raise_for_status()

        except httpx.RequestError:
            failed_providers.append(provider)

        except httpx.HTTPStatusError:
            failed_providers.append(provider)

    if failed_providers:
        raise FlowRuntimeError(
            f"Notification failed for: {', '.join(failed_providers)}",
            line,
            col,
        )

    return None


# -------------------------
# Runtime Operations
# -------------------------


def builtin_log(args, interpreter, line=0, col=0):

    if len(args) != 1:
        raise FlowRuntimeError(
            "log() expects exactly one argument.",
            line,
            col
        )

    value = args[0]

    # Convert values into readable strings.
    if isinstance(value, str):
        message = value
    else:
        try:
            message = json.dumps(
                value,
                ensure_ascii=False,
                default=repr
            )
        except Exception:
            try:
                message = repr(value)
            except Exception:
                message = f"<unserializable {type(value).__name__}>"

    # Limit message size to 10 KB (characters).
    max_length = 10_000
    truncated = len(message) > max_length

    if truncated:
        suffix = "... [truncated]"
        message = message[:max_length - len(suffix)] + suffix

    # Emit the user-facing log event.
    interpreter.emit_log({
        "type": "user_log",
        "step": interpreter.current_step,
        "message": message,
        "status": "success",
        "line": line,
        "col": col,
        "truncated": truncated,
        "timestamp": time.time(),
    })

    return {
        "success": True,
        "operation": "log",
        "message": message,
        "truncated": truncated,
    }



def builtin_wait(args, interpreter, line=0, col=0):
    import time

    time.sleep(args[0])

    return {
        "success": True,
        "operation": "wait",
        "seconds": args[0],
    }



def builtin_retry(args, interpreter, line=0, col=0):

    # Validate argument count.
    if len(args) != 1:
        raise FlowRuntimeError(
            "retry() expects exactly one argument.",
            line,
            col
        )

    attempts = args[0]

    # Validate integer argument.
    if not isinstance(attempts, int) or isinstance(attempts, bool):
        raise FlowRuntimeError(
            "retry() expects an integer number of attempts.",
            line,
            col
        )

    # Limit retries between 0 and 10.
    if attempts < 0 or attempts > 10:
        raise FlowRuntimeError(
            "Retry attempts must be between 0 and 10.",
            line,
            col
        )

    # retry() is only allowed inside on_fail.
    if not interpreter.in_on_fail:
        raise FlowRuntimeError(
            "retry() can only be called inside an on_fail block.",
            line,
            col
        )

    # Do not request another retry after the limit is exhausted.
    if interpreter.retry_disabled:
        return None

    # Signal the interpreter to retry the step.
    raise RetrySignal(attempts)


def builtin_print(args, interpreter, line=0, col=0):
    print(*args)
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