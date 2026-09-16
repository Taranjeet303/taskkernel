# flowscript/builtins.py


# -------------------------
# HTTP Operations
# -------------------------

def builtin_http_get(args, interpreter):
    return {
        "status": 200,
        "body": {"fake": "response"},
        "url": args[0],
        "method": "GET",
    }


def builtin_http_post(args, interpreter):
    return {
        "status": 201,
        "body": {"fake": "created"},
        "url": args[0],
        "method": "POST",
        "request_body": args[1],
    }


def builtin_http_put(args, interpreter):
    return {
        "status": 200,
        "body": {"fake": "updated"},
        "url": args[0],
        "method": "PUT",
        "request_body": args[1],
    }


def builtin_http_patch(args, interpreter):
    return {
        "status": 200,
        "body": {"fake": "patched"},
        "url": args[0],
        "method": "PATCH",
        "request_body": args[1],
    }


def builtin_http_delete(args, interpreter):
    return {
        "status": 204,
        "body": None,
        "url": args[0],
        "method": "DELETE",
    }


# -------------------------
# Database Operations
# -------------------------

def builtin_db_query(args, interpreter):
    return {
        "success": True,
        "query": args[0],
        "rows": [],
    }


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