# FlowScript Language Specification

**Platform:** TaskKernel  
**Language:** FlowScript  
**File Extension:** `.flow`  
**Current Version:** 1.0 (Draft)  
**Status:** Under Development

---

## Table of Contents

1. Introduction
2. Language Overview
3. Lexical Structure
4. Data Types
5. Variables
6. Operators
7. Expressions
8. Statements
9. Blocks
10. Control Flow
11. Tasks
12. Built-in Functions
13. Runtime Model
14. Program Structure
15. Formal Grammar (EBNF)
16. Error Handling
17. Unsupported Features
18. Complete Example
19. Conclusion

---

## 1. Introduction

FlowScript is a domain-specific scripting language (DSL) designed for defining backend automation workflows. It serves as the scripting language for TaskKernel, a backend workflow execution platform that interprets and executes workflow scripts against backend services such as HTTP APIs, databases, caches, and notification systems.

Unlike general-purpose programming languages, FlowScript focuses on workflow orchestration rather than application development. The language provides a concise syntax for describing backend operations, control flow, and reusable tasks without requiring large amounts of boilerplate code.

FlowScript is intentionally designed to remain small, readable, and predictable. Version 1.0 includes only the language constructs required for backend workflow execution and intentionally excludes features unrelated to its primary purpose.

This document defines the syntax, language rules, execution model, and built-in functionality available in FlowScript Version 1.0.

### Design Goals

- Provide a readable language for backend workflow automation.
- Minimize repetitive orchestration code.
- Offer built-in support for common backend operations.
- Keep the language intentionally small and easy to understand.
- Execute workflows through the TaskKernel runtime.

### Intended Use Cases

- Backend workflow automation
- API orchestration
- Database operations
- Background task execution
- Event-driven workflows

---

## 2. Language Overview

FlowScript is an interpreted, statement-based programming language designed specifically for backend workflow automation. A FlowScript program consists of one or more workflow definitions (`flow`) containing executable statements, reusable tasks, and workflow steps.

Each `.flow` file is parsed and executed by the TaskKernel runtime. During execution, the runtime evaluates statements sequentially while maintaining variable scope, execution state, and runtime metadata.

FlowScript includes built-in operations for interacting with backend infrastructure such as HTTP services, PostgreSQL databases, Redis, and notification providers. These operations are exposed as language-level functions, allowing workflow logic to remain concise and readable.

### Characteristics

- Interpreted language
- Statement-based execution
- Domain-specific language (DSL)
- Workflow-oriented design
- Built-in backend operations
- Block-based syntax using curly braces (`{}`)
- Designed to execute within the TaskKernel runtime

---

## 3. Lexical Structure

The lexical structure of FlowScript defines how source code is broken into individual tokens before parsing begins. During lexical analysis, the FlowScript lexer scans the source file from left to right and converts the input into a sequence of tokens such as keywords, identifiers, literals, operators, and punctuation symbols.

The lexer ignores whitespace and comments where they do not affect program structure. Each token produced by the lexer is later consumed by the parser to construct the program's Abstract Syntax Tree (AST).

---

### 3.1 Keywords

Keywords are reserved words that have predefined meanings within the language and cannot be used as identifiers.

#### Language Keywords

| Keyword | Description |
|----------|-------------|
| `flow` | Declares a workflow definition. |
| `task` | Declares a reusable task. |
| `step` | Declares a named workflow step. |
| `let` | Declares a variable. |
| `if` | Begins a conditional statement. |
| `else` | Specifies the alternative branch of a conditional statement. |
| `while` | Begins a while loop. |
| `for` | Begins a for loop. |
| `in` | Specifies the iterable used by a for loop. |
| `return` | Returns a value from a task. |
| `on_fail` | Defines failure handling for a workflow step. |
| `true` | Boolean literal representing logical true. |
| `false` | Boolean literal representing logical false. |
| `and` | Logical AND operator. |
| `or` | Logical OR operator. |
| `not` | Logical NOT operator. |

> Reserved keywords cannot be used as variable names, task names, or identifiers.

---

### 3.2 Identifiers

Identifiers are user-defined names used to reference variables, tasks, and workflow definitions.

#### Rules

- Must begin with an alphabetic character (`A-Z` or `a-z`) or an underscore (`_`).
- May contain letters, digits (`0-9`), and underscores.
- Are case-sensitive.
- Cannot be a reserved keyword.

#### Valid Identifiers

```flowscript
user
user_name
customer123
_api
processOrder
```

#### Invalid Identifiers

```flowscript
123user
flow
task
user-name
```

---

### 3.3 Literals

Literals represent constant values written directly in source code.

FlowScript Version 1.0 supports the following literal types:

| Literal Type | Example |
|---------------|---------|
| Number | `42`, `3.14` |
| String | `"Hello"` |
| Boolean | `true`, `false` |
| List | `[1, 2, 3]` |
| Record | `{ "name": "Alice" }` |

---

### 3.4 Operators

Operators are symbols or keywords used to perform arithmetic, comparison, logical, and assignment operations.

The complete list of supported operators is defined in **Section 6 – Operators**.

---

### 3.5 Delimiters

FlowScript uses the following punctuation symbols to separate and organize language constructs.

| Symbol | Purpose |
|---------|----------|
| `(` `)` | Function calls and grouped expressions |
| `{` `}` | Blocks and record literals |
| `[` `]` | List literals |
| `,` | Separates parameters and list elements |
| `:` | Type annotations and record key-value pairs |
| `=` | Variable assignment |

---

### 3.6 Comments

Single-line comments begin with the `#` character.

Everything following `#` until the end of the current line is ignored by the lexer.

#### Example

```flowscript
# Create a new user

let username = "Alice"
```

FlowScript Version 1.0 does not support multi-line comments.

---

### 3.7 Whitespace

Whitespace includes spaces, tabs, and newline characters.

Whitespace is generally ignored by the lexer except where it separates adjacent tokens or improves readability.

FlowScript statements are separated by newline characters. Additional whitespace may be used to improve formatting but does not change program behavior.

---

## 4. Data Types

FlowScript is a statically recognizable, dynamically evaluated language that supports a small set of built-in data types required for backend workflow automation. These types are sufficient for representing values commonly encountered while interacting with APIs, databases, and workflow metadata.

Version 1.0 supports five built-in data types.

---

### 4.1 Number

The `Number` type represents numeric values. Both integer and decimal values are represented using the same type.

#### Examples

```flowscript
let age: Number = 25

let price: Number = 199.99

let retries: Number = 3
```

#### Supported Operations

- Addition (`+`)
- Subtraction (`-`)
- Multiplication (`*`)
- Division (`/`)
- Comparison (`==`, `!=`, `<`, `>`, `<=`, `>=`)

---

### 4.2 String

The `String` type represents textual data enclosed within double quotation marks.

#### Examples

```flowscript
let username: String = "Alice"

let message: String = "Workflow completed"

let endpoint: String = "/users"
```

#### Supported Operations

- Assignment
- Equality comparison
- String concatenation using `+`

---

### 4.3 Boolean

The `Boolean` type represents logical values.

FlowScript supports two boolean literals:

- `true`
- `false`

#### Examples

```flowscript
let success: Boolean = true

let authenticated: Boolean = false
```

Boolean values are commonly used in conditional statements and logical expressions.

---

### 4.4 List

The `List` type represents an ordered collection of values.

Lists may contain zero or more elements.

#### Examples

```flowscript
let numbers: List = [1, 2, 3]

let users: List = ["Alice", "Bob", "Charlie"]

let empty: List = []
```

Lists are primarily intended for iteration using `for` loops.

---

### 4.5 Record

The `Record` type represents a collection of key-value pairs.

Records are commonly used to represent structured data returned from APIs or database operations.

#### Examples

```flowscript
let user: Record = {

    "id": 1,

    "name": "Alice",

    "active": true

}
```

Records may contain values of any supported FlowScript data type.

---

### Type Annotations

Variable declarations may optionally include a type annotation.

Type annotations improve code readability and allow the runtime to provide clearer validation and error messages.

#### Syntax

```flowscript
let username: String = "Alice"

let age: Number = 20

let enabled: Boolean = true
```

Type annotations are optional in FlowScript Version 1.0.

---

### Summary

| Type | Description |
|------|-------------|
| `Number` | Numeric values |
| `String` | Text values |
| `Boolean` | Logical values |
| `List` | Ordered collection of values |
| `Record` | Key-value structured data |

---

## 5. Variables

Variables are used to store values that can be referenced and modified throughout the execution of a workflow. Every variable is identified by a unique name (identifier) and may optionally include a type annotation.

Variables are declared using the `let` keyword.

---

### Declaration

A variable declaration creates a new variable and assigns it an initial value.

#### Syntax

```flowscript
let identifier = expression

let identifier: Type = expression
```

#### Examples

```flowscript
let username = "Alice"

let age: Number = 25

let active: Boolean = true

let users: List = []

let profile: Record = {}
```

---

### Assignment

After declaration, an existing variable may be assigned a new value using the assignment operator (`=`).

#### Syntax

```flowscript
identifier = expression
```

#### Example

```flowscript
let retries = 1

retries = retries + 1
```

Assignment updates the value stored in the variable without creating a new variable.

---

### Scope

Variables are visible only within the block in which they are declared.

Variables declared inside a nested block are not accessible outside that block.

#### Example

```flowscript
let message = "Start"

if true {

    let status = "Running"

}

log(message)

log(status)    # Invalid
```

In the example above, `message` remains accessible after the `if` block, while `status` is limited to the scope in which it was declared.

---

### Naming Rules

Variable names must follow the identifier rules defined in **Section 3.2 – Identifiers**.

Examples of valid variable names:

```flowscript
username

retry_count

user1

_api
```

Examples of invalid variable names:

```flowscript
1user

flow

task

user-name
```

---

### Type Annotations

FlowScript supports optional type annotations.

When present, a type annotation describes the expected type of the variable and may be used by the runtime to improve validation and error reporting.

#### Example

```flowscript
let username: String = "Alice"

let age: Number = 20

let success: Boolean = true

let users: List = []

let record: Record = {}
```

Type annotations are optional in FlowScript Version 1.0.

---

### Best Practices

- Use descriptive variable names.
- Keep variable scope as small as possible.
- Use type annotations where they improve readability.
- Avoid reusing variable names within the same scope.

---

---

## 6. Operators

Operators perform arithmetic, comparison, logical, and assignment operations on values. FlowScript Version 1.0 provides a small set of operators required for backend workflow automation.

---

### 6.1 Arithmetic Operators

Arithmetic operators are used with numeric values.

| Operator | Description | Example |
|----------|-------------|---------|
| `+` | Addition | `a + b` |
| `-` | Subtraction | `a - b` |
| `*` | Multiplication | `a * b` |
| `/` | Division | `a / b` |

#### Example

```flowscript
let total = price + tax

let average = total / count

let retries = retries + 1
```

---

### 6.2 Comparison Operators

Comparison operators compare two values and produce a boolean result.

| Operator | Description |
|----------|-------------|
| `==` | Equal to |
| `!=` | Not equal to |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal to |
| `>=` | Greater than or equal to |

#### Example

```flowscript
if retries > 3 {

    log("Maximum retries reached")

}
```

---

### 6.3 Logical Operators

Logical operators combine or negate boolean expressions.

| Operator | Description |
|----------|-------------|
| `and` | Logical AND |
| `or` | Logical OR |
| `not` | Logical NOT |

#### Example

```flowscript
if authenticated and verified {

    send_notification("Access granted")

}
```

---

### 6.4 Assignment Operator

The assignment operator (`=`) assigns the result of an expression to a variable.

#### Example

```flowscript
let retries = 1

retries = retries + 1
```

The assignment operator updates the value stored in an existing variable.

---

### Operator Precedence

FlowScript evaluates expressions according to the following precedence (highest to lowest):

| Precedence | Operators |
|------------|-----------|
| Highest | `not`, unary `-` |
| | `*`, `/` |
| | `+`, `-` |
| | `<`, `>`, `<=`, `>=` |
| | `==`, `!=` |
| Lowest | `and`, `or` |

Parentheses may be used to explicitly control evaluation order.

#### Example

```flowscript
let result = (price + tax) * quantity
```

---

---

## 7. Expressions

An expression is a combination of values, variables, operators, or function calls that evaluates to a single result.

Expressions are commonly used in variable declarations, assignments, conditional statements, loop conditions, function arguments, and return statements.

---

### 7.1 Literal Expressions

A literal expression consists of a single literal value.

#### Examples

```flowscript
42

3.14

"Hello"

true

[1, 2, 3]

{
    "name": "Alice"
}
```

---

### 7.2 Variable Expressions

A variable expression evaluates to the value currently stored in a variable.

#### Example

```flowscript
let retries = 3

retries
```

---

### 7.3 Arithmetic Expressions

Arithmetic expressions combine numeric values using arithmetic operators.

#### Examples

```flowscript
price + tax

total - discount

quantity * price

total / count
```

Parentheses may be used to control evaluation order.

```flowscript
(price + tax) * quantity
```

---

### 7.4 Comparison Expressions

Comparison expressions compare two values and evaluate to a Boolean result.

#### Examples

```flowscript
status == 200

retries < 3

count >= limit
```

---

### 7.5 Logical Expressions

Logical expressions combine Boolean expressions using logical operators.

#### Examples

```flowscript
authenticated and verified

retries < 3 or force_retry

not success
```

Logical expressions evaluate to either `true` or `false`.

---

### 7.6 Function Call Expressions

Calling a task or built-in function is itself an expression.

The return value of the function becomes the value of the expression.

#### Examples

```flowscript
http_get("/users")

db_query("SELECT * FROM users")

send_notification("Workflow completed")
```

Function calls may also appear within larger expressions.

```flowscript
let response = http_get("/users")

let success = response.status == 200
```

---

### 7.7 List Expressions

List expressions create ordered collections of values.

#### Examples

```flowscript
[]

[1, 2, 3]

["Alice", "Bob", "Charlie"]
```

Lists may contain any supported FlowScript values.

---

### 7.8 Record Expressions

Record expressions create key-value collections.

#### Example

```flowscript
{
    "name": "Alice",
    "age": 20,
    "active": true
}
```

Record values may contain any supported FlowScript data type.

---

### 7.9 Parenthesized Expressions

Parentheses group expressions and explicitly control evaluation order.

#### Example

```flowscript
(price + tax) * quantity
```

---

### Expression Evaluation

Expressions are evaluated according to the operator precedence defined in **Section 6 – Operators**.

Complex expressions are evaluated recursively until a single value is produced.

---

## 8. Statements

A statement represents a single executable instruction in a FlowScript program. Workflows are composed of one or more statements, which are executed sequentially by the TaskKernel runtime unless control flow modifies the execution order.

Each statement performs a specific action such as declaring a variable, assigning a value, invoking a task, or controlling workflow execution.

---

### 8.1 Variable Declaration Statement

A variable declaration creates a new variable and assigns it an initial value.

#### Syntax

```flowscript
let identifier = expression
```

#### Example

```flowscript
let retries = 3

let endpoint = "/users"

let response = http_get(endpoint)
```

---

### 8.2 Assignment Statement

An assignment statement updates the value stored in an existing variable.

#### Syntax

```flowscript
identifier = expression
```

#### Example

```flowscript
retries = retries + 1
```

The variable must already exist before it can be assigned a new value.

---

### 8.3 Task Call Statement

A task call executes either a user-defined task or a built-in function.

#### Examples

```flowscript
send_notification("Workflow started")

http_get("/users")

db_insert("users", user)
```

If the called task returns a value, it may be assigned to a variable.

```flowscript
let response = http_get("/users")
```

---

### 8.4 Return Statement

The `return` statement immediately exits the current task and optionally returns a value to the caller.

#### Syntax

```flowscript
return

return expression
```

#### Examples

```flowscript
return
```

```flowscript
return response
```

The `return` statement is valid only inside a task definition.

---

### 8.5 Conditional Statement

Conditional statements execute a block of code only when a specified condition evaluates to `true`.

FlowScript provides the following conditional statements:

- `if`
- `if ... else`

Conditional statements are described in detail in **Section 10 – Control Flow**.

---

### 8.6 Loop Statements

Loop statements repeatedly execute a block of code while a condition remains true or while iterating over a collection.

FlowScript supports:

- `while`
- `for`

Loop behavior is described in **Section 10 – Control Flow**.

---

### Statement Execution

Unless modified by control flow, statements are executed sequentially from top to bottom.

For example,

```flowscript
let response = http_get("/users")

db_insert("logs", response)

send_notification("Workflow completed")
```

The runtime executes these statements in the following order:

1. Perform the HTTP request.
2. Store the response.
3. Send the notification.

---

## 9. Blocks

A block is a group of one or more statements enclosed within curly braces (`{}`).

Blocks are used to organize executable code and define the scope of variables declared within them.

FlowScript uses blocks to define workflow bodies, tasks, workflow steps, conditional statements, and loops.

---

### Block Syntax

```flowscript
{
    statement
    statement
    statement
}
```

---

### Block Scope

Variables declared inside a block are only accessible within that block.

#### Example

```flowscript
let workflow_name = "User Import"

if true {

    let retries = 3

    log(retries)

}

log(workflow_name)
```

In the example above:

- `workflow_name` remains accessible after the `if` block.
- `retries` exists only within the `if` block.

---

### Nested Blocks

Blocks may be nested inside other blocks.

Each nested block creates its own scope.

#### Example

```flowscript
flow user_sync {

    step "Fetch Users" {

        if retries < 3 {

            log("Retrying request")

        }

    }

}
```

Each nested block is executed within the context of its enclosing block.

---

### Block Usage

Blocks are used by the following language constructs:

| Construct | Purpose |
|-----------|---------|
| `flow` | Defines a workflow. |
| `task` | Defines a reusable task. |
| `step` | Groups related workflow operations. |
| `if` | Defines conditional execution. |
| `else` | Defines the alternative execution path. |
| `while` | Defines a conditional loop. |
| `for` | Defines an iteration block. |

---

### Empty Blocks

A block may contain zero statements.

#### Example

```flowscript
step "Reserved for Future" {

}
```

Although valid, empty blocks are generally intended as placeholders during development.

---

## 10. Control Flow

Control flow statements determine the order in which statements are executed. By default, FlowScript executes statements sequentially from top to bottom. Control flow constructs allow workflows to make decisions and repeat operations based on runtime conditions.

FlowScript Version 1.0 provides the following control flow constructs:

- `if`
- `if ... else`
- `while`
- `for`

---

### 10.1 If Statement

The `if` statement executes a block only if its condition evaluates to `true`.

#### Syntax

```flowscript
if expression {

    ...

}
```

#### Example

```flowscript
if response.status == 200 {

    log("Request completed successfully")

}
```

If the condition evaluates to `false`, the block is skipped.

---

### 10.2 If-Else Statement

The `else` block provides an alternative execution path when the `if` condition evaluates to `false`.

#### Syntax

```flowscript
if expression {

    ...

}
else {

    ...

}
```

#### Example

```flowscript
if response.status == 200 {

    log("User imported successfully")

}
else {

    send_notification("User import failed")

}
```

Exactly one of the two blocks is executed.

---

### 10.3 While Loop

The `while` loop repeatedly executes a block as long as its condition evaluates to `true`.

#### Syntax

```flowscript
while expression {

    ...

}
```

#### Example

```flowscript
let retries = 0

while retries < 3 {

    http_get("/health")

    retries = retries + 1

}
```

The loop condition is evaluated before each iteration.

If the condition is initially `false`, the loop body is not executed.

---

### 10.4 For Loop

The `for` loop iterates over every element in a list.

#### Syntax

```flowscript
for variable in expression {

    ...

}
```

#### Example

```flowscript
let users = ["Alice", "Bob", "Charlie"]

for user in users {

    send_notification(user)

}
```

During each iteration, the loop variable is assigned the current element from the list.

---

### Nested Control Flow

Control flow statements may be nested inside one another.

#### Example

```flowscript
for user in users {

    if user.active {

        send_notification(user.email)

    }

}
```

Nested control flow allows workflows to express more complex execution logic while maintaining readability.

---

### Notes

- Conditions must evaluate to a Boolean value.
- Loops execute until their termination condition is met.
- Variables declared inside a control flow block are scoped to that block.
- Control flow constructs may contain any valid FlowScript statements.

---

## 11. Tasks

Tasks define reusable units of executable logic within a workflow. A task may accept zero or more parameters, execute a sequence of statements, and optionally return a value.

Unlike general-purpose programming languages that define reusable logic using functions, FlowScript uses the `task` keyword to emphasize that reusable units represent backend operations performed within a workflow.

Tasks are declared inside a `flow` definition and may be invoked from any step or other task within the same workflow.

---

### Task Declaration

Tasks are declared using the `task` keyword followed by a unique task name.

#### Syntax

```flowscript
task task_name(parameters) {

    ...

}
```

#### Example

```flowscript
task fetch_users() {

    let response = http_get("/users")

    return response

}
```

---

### Parameters

Tasks may define zero or more parameters.

Parameters allow values to be passed into a task during execution.

#### Example

```flowscript
task send_email(email, message) {

    send_notification(email, message)

}
```

Parameters behave like local variables and are accessible only within the task body.

---

### Calling a Task

Tasks are invoked by their name followed by parentheses.

Arguments supplied during the call are assigned to the task's parameters.

#### Example

```flowscript
task create_user(email) {

    let result = db_insert("users", {

        "email": email

    })

    return result

}

let user = create_user("alice@example.com")
```

---

### Return Values

A task may optionally return a value using the `return` statement.

The returned value becomes the result of the task call.

#### Example

```flowscript
task fetch_status() {

    return http_get("/status")

}

let status = fetch_status()
```

If no value is returned, the task completes without producing a result.

---

### Task Scope

Tasks declared within a flow are available throughout that flow.

Variables declared inside a task remain local to that task and are not accessible outside its scope.

---

### Best Practices

- Keep tasks focused on a single responsibility.
- Use descriptive task names.
- Return values when task results are needed by subsequent workflow steps.
- Avoid placing unrelated operations within the same task.

---

## 12. Built-in Functions

FlowScript provides a collection of built-in functions for interacting with backend services and the TaskKernel runtime. These functions are implemented by the runtime and are available to every workflow without requiring additional imports or configuration.

Built-in functions simplify common backend operations such as making HTTP requests, interacting with databases, publishing events, sending notifications, logging execution details, and controlling workflow execution.

---

### 12.1 HTTP Operations

HTTP functions allow workflows to communicate with external HTTP services.

#### Supported Functions

```flowscript
http_get(url)

http_post(url, body)

http_put(url, body)

http_patch(url, body)

http_delete(url)
```

#### Example

```flowscript
let users = http_get("/users")

http_post("/users", {
    "name": "Alice"
})

http_put("/users/1", {
    "active": true
})

http_patch("/users/1", {
    "email": "alice@example.com"
})

http_delete("/users/1")
```

---

### 12.2 Database Operations

Database functions allow workflows to interact with the configured relational database.

#### Supported Functions

```flowscript
db_query(query)

db_insert(table, record)

db_update(table, record, updates)

db_delete(table, condition)
```

#### Example

```flowscript
let user = db_query("SELECT * FROM users")

db_insert("users", {
    "name": "Alice"
})

db_update("users", {
    "id": 1
}, {
    "active": true
})

db_delete("users", {
    "id": 1
})
```

---

### 12.3 Event Operations

Event functions publish messages that can be consumed by other services or workflows.

#### Supported Functions

```flowscript
publish_event(channel, message)
```

#### Example

```flowscript
publish_event(
    "user.created",
    {
        "id": 1,
        "email": "alice@example.com"
    }
)
```

The underlying event system is managed by the TaskKernel runtime.

---

### 12.4 Notification Operations

Notification functions send messages through the notification provider configured within TaskKernel.

#### Supported Functions

```flowscript
notify(message)
```

#### Example

```flowscript
notify("Workflow completed successfully")
```

The notification destination depends on the TaskKernel runtime configuration.

---

### 12.5 Runtime Functions

Runtime functions provide utilities for controlling workflow execution and recording runtime information.

#### Logging

```flowscript
log(message)
```

##### Example

```flowscript
log("Starting user synchronization")
```

The `log()` function records execution information in the workflow execution logs.

---

#### Wait

```flowscript
wait(seconds)
```

##### Example

```flowscript
wait(5)
```

Execution pauses for the specified duration before continuing.

---

#### Retry

```flowscript
retry(attempts)
```

##### Example

```flowscript
retry(3)
```

The behavior of `retry()` depends on the surrounding execution context and failure handling rules.

---

### Return Values

Some built-in functions return values that may be assigned to variables.

#### Example

```flowscript
let response = http_get("/users")

let users = db_query("SELECT * FROM users")
```

Other built-in functions perform an action without returning a value.

Examples include:

- `http_post()`
- `http_put()`
- `http_patch()`
- `http_delete()`
- `db_insert()`
- `db_update()`
- `db_delete()`
- `publish_event()`
- `notify()`
- `log()`
- `wait()`
- `retry()`

---

### Notes

- Built-in functions are available to every FlowScript workflow.
- Built-in functions are implemented by the TaskKernel runtime.
- Built-in function names are reserved and cannot be redefined.
- Runtime behavior is described further in **Section 13 – Runtime Model**.

---

## 13. Runtime Model

The TaskKernel runtime is responsible for executing FlowScript workflows. When a `.flow` script is submitted, the runtime processes the script through multiple execution stages before interacting with backend services.

Each workflow execution is isolated and maintains its own execution state, including variables, task calls, execution logs, and runtime metadata.

---

### Execution Lifecycle

A FlowScript workflow is executed in the following stages:

1. Source code is received by the TaskKernel execution service.
2. The lexer converts the source code into a sequence of tokens.
3. The parser validates the syntax and constructs an Abstract Syntax Tree (AST).
4. The interpreter traverses the AST and evaluates each statement.
5. Built-in operations interact with backend services through the TaskKernel runtime.
6. Execution logs and workflow metadata are recorded.
7. The workflow completes with either a successful result or an execution error.

---

### Execution State

During execution, the runtime maintains the current state of the workflow.

Execution state includes:

- Variable values
- Task execution context
- Current execution step
- Runtime metadata
- Execution status

The execution state exists only for the lifetime of the workflow execution.

---

### Execution Order

Unless modified by control flow statements, FlowScript executes statements sequentially from top to bottom.

For example,

```flowscript
let response = http_get("/users")

db_insert("logs", response)

notify("Workflow completed")
```

Execution occurs in the following order:

1. Perform the HTTP request.
2. Store the response in the database.
3. Send the notification.

---

### Runtime Responsibilities

The TaskKernel runtime is responsible for:

- Evaluating expressions
- Managing variable scope
- Executing tasks
- Executing built-in operations
- Recording execution logs
- Handling runtime errors
- Maintaining execution state

---

### Workflow Isolation

Each workflow execution is independent.

Variables, execution state, and runtime information created during one execution are not shared with other workflow executions.

This allows multiple workflows to execute without affecting one another.

---

### Backend Integration

The runtime provides the implementation of all built-in operations supported by FlowScript.

Depending on the workflow, the runtime may interact with:

- HTTP services
- Relational databases
- Event systems
- Notification providers

FlowScript itself defines **what** should be executed, while the TaskKernel runtime determines **how** those operations are performed.

               FlowScript Source (.flow)
                         │
                         ▼
                      Lexer
                         │
                         ▼
                      Tokens
                         │
                         ▼
         Recursive Descent Parser
                         │
                         ▼
            Abstract Syntax Tree (AST)
                         │
                         ▼
             Tree-Walking Interpreter
                         │
                         ▼
                 TaskKernel Runtime
        ┌────────────┬────────────┬────────────┬────────────┐
        ▼            ▼            ▼            ▼
   HTTP Services  Database     Event System  Notifications

---

## 14. Program Structure

A FlowScript source file (`.flow`) defines one or more workflows. Each workflow serves as the top-level executable unit and contains reusable tasks, workflow steps, and executable statements.

The overall structure of a FlowScript program is designed to keep workflow logic organized, readable, and easy to maintain.

---

### General Structure

A workflow consists of the following components:

- A `flow` declaration.
- Zero or more task definitions.
- One or more workflow steps.
- Executable statements contained within workflow steps.

The following illustrates the typical organization of a FlowScript program.

```flowscript
flow workflow_name {

    task reusable_task(parameters) {

        ...

    }

    step "Step Name" {

        ...

    }

    step "Another Step" {

        ...

    }

}
```

---

### Workflow

A `flow` represents the top-level executable unit of a FlowScript program.

Each workflow has a unique name and serves as the entry point for execution.

#### Example

```flowscript
flow user_import {

    ...

}
```

---

### Tasks

Tasks define reusable units of logic that may be invoked multiple times within the same workflow.

Task definitions are declared before they are used by workflow steps.

#### Example

```flowscript
task fetch_users() {

    return http_get("/users")

}
```

---

### Steps

Steps divide a workflow into logical execution stages.

Each step groups related operations and provides meaningful checkpoints for execution logging and debugging.

#### Example

```flowscript
step "Fetch Users" {

    let users = fetch_users()

}
```

---

### Execution Order

When a workflow is executed, TaskKernel processes its contents in the following order:

1. The workflow is initialized.
2. Task definitions become available for invocation.
3. Workflow steps are executed sequentially from top to bottom.
4. Statements within each step are executed according to the language's execution rules.

---

### Recommended Organization

For improved readability, FlowScript programs should generally follow this structure:

1. Workflow declaration.
2. Task definitions.
3. Workflow steps.
4. Workflow completion.

Although formatting is flexible, maintaining a consistent structure improves readability and simplifies maintenance.

---

## 15. Formal Grammar (EBNF)

This section defines the formal syntax of **FlowScript Version 1.0** using **Extended Backus–Naur Form (EBNF)**. The grammar serves as the authoritative reference for the FlowScript parser and specifies the valid syntactic structure of FlowScript programs.

The recursive descent parser implemented by **TaskKernel** follows the grammar defined in this section. Any FlowScript source code accepted by the parser must conform to these rules.

```ebnf
(* ========================================================== *)
(* FlowScript Formal Grammar (EBNF) — Version 1.0             *)
(* ========================================================== *)


(* ===================== PROGRAM STRUCTURE ===================== *)

program        := flow_def+

flow_def       := "flow" IDENTIFIER "{" NEWLINE
                   (step_def | task_def | statement)*
                   "}" NEWLINE

step_def       := "step" STRING block on_fail_clause?

task_def       := "task" IDENTIFIER "(" params? ")" block

on_fail_clause := "on_fail" block


(* ===================== STATEMENTS ===================== *)

statement      := let_stmt
                 | assign_stmt
                 | if_stmt
                 | while_stmt
                 | for_stmt
                 | return_stmt
                 | expr_stmt

let_stmt       := "let" IDENTIFIER (":" IDENTIFIER)? "=" expression NEWLINE

assign_stmt    := IDENTIFIER "=" expression NEWLINE

if_stmt        := "if" expression block
                   ("else" block)?

while_stmt     := "while" expression block

for_stmt       := "for" IDENTIFIER "in" expression block

return_stmt    := "return" expression? NEWLINE

expr_stmt      := expression NEWLINE

block          := "{" NEWLINE
                   statement*
                   "}" NEWLINE


(* ===================== EXPRESSIONS ===================== *)

expression     := logical_or

logical_or     := logical_and
                  ("or" logical_and)*

logical_and    := equality
                  ("and" equality)*

equality       := comparison
                  (("==" | "!=") comparison)*

comparison     := term
                  (("<" | ">" | "<=" | ">=") term)*

term           := factor
                  (("+" | "-") factor)*

factor         := unary
                  (("*" | "/") unary)*

unary          := ("not" | "-") unary
                 | call

call           := primary
                  (("." IDENTIFIER) | ("(" arguments? ")"))*

primary        := NUMBER
                 | STRING
                 | "true"
                 | "false"
                 | IDENTIFIER
                 | "(" expression ")"
                 | list_literal
                 | record_literal

arguments      := expression
                  ("," expression)*


(* ===================== COLLECTION LITERALS ===================== *)

list_literal   := "["
                  (expression ("," expression)*)?
                  "]"

record_literal := "{"
                  (STRING ":" expression
                  ("," STRING ":" expression)*)?
                  "}"


(* ===================== PARAMETERS ===================== *)

params         := param
                  ("," param)*

param          := IDENTIFIER


(* ===================== LEXICAL STRUCTURE ===================== *)

IDENTIFIER     := LETTER
                  (LETTER | DIGIT | "_")*

NUMBER         := DIGIT+
                  ("." DIGIT+)?

STRING         := '"'
                  (any character except '"')*
                  '"'

LETTER         := "a".."z"
                 | "A".."Z"

DIGIT          := "0".."9"

COMMENT        := "#"
                  (any character except NEWLINE)*
```

The grammar presented above defines the complete syntax supported by **FlowScript Version 1.0**. It serves as the reference specification for the language and guides the implementation of the FlowScript lexer, recursive descent parser, and interpreter within the TaskKernel runtime.

---

## 16. Error Handling

FlowScript distinguishes between **syntax errors** and **runtime errors**. Syntax errors are detected before execution begins, while runtime errors occur during workflow execution when evaluating expressions or invoking built-in operations.

When an error occurs, the TaskKernel runtime attempts to provide clear diagnostic information to help identify and resolve the issue.

---

### 16.1 Syntax Errors

Syntax errors occur when the source code does not conform to the FlowScript grammar.

Examples include:

- Missing or unmatched braces
- Missing parentheses
- Unexpected tokens
- Invalid statements
- Missing identifiers
- Malformed expressions

#### Example

```flowscript
flow user_import {

    let response =

}
```

Since the variable declaration is incomplete, the parser reports a syntax error and workflow execution does not begin.

---

### 16.2 Runtime Errors

Runtime errors occur after a workflow has been successfully parsed and execution has started.

Examples include:

- Failed HTTP requests
- Database operation failures
- Calling an undefined task
- Accessing an undefined variable
- Invalid operation on a value
- Failure within a built-in function

#### Example

```flowscript
let response = http_get("/invalid-endpoint")
```

If the HTTP request cannot be completed successfully, the runtime reports a runtime error.

---

### 16.3 Error Reporting

Whenever possible, FlowScript reports useful diagnostic information for each error.

Diagnostic information may include:

- Error category
- Error message
- Line number
- Column number
- Source location

Providing precise diagnostics helps identify the location and cause of an error within a workflow.

---

### 16.4 Execution Behavior

If a syntax error is encountered, workflow execution is terminated before interpretation begins.

If a runtime error occurs during execution, the current workflow execution is stopped and the error is reported by the TaskKernel runtime.

Future versions of FlowScript may introduce additional error recovery mechanisms and configurable failure handling.

---

## 17. Unsupported Features

FlowScript Version 1.0 is intentionally designed as a focused domain-specific language (DSL) for backend workflow automation. To keep the language simple, predictable, and easy to implement, several features commonly found in general-purpose programming languages are intentionally excluded.

The absence of these features is a deliberate design decision rather than a limitation of the language.

---

### Unsupported Language Features

The following features are **not supported** in FlowScript Version 1.0:

- Classes and object-oriented programming
- Modules and import statements
- Exception handling (`try`, `catch`, `finally`)
- Lambda or anonymous functions
- User-defined operators
- Operator overloading
- Generics
- Inheritance and polymorphism
- User-defined data types
- Multi-line comments
- Asynchronous language constructs (`async` / `await`)
- Concurrency primitives

---

### Design Philosophy

FlowScript is designed to describe backend workflows rather than serve as a general-purpose programming language.

Version 1.0 focuses on providing a concise and readable syntax for:

- Defining workflows
- Organizing reusable tasks
- Executing backend operations
- Controlling workflow execution
- Integrating with backend services through built-in operations

Features that do not directly support these goals have been intentionally excluded.

---

### Future Evolution

Some unsupported features may be considered for future versions of FlowScript if they improve the language without compromising its simplicity or workflow-oriented design.

The inclusion of a feature in future versions is not guaranteed.

   ---

## 18. Complete Example

The following example demonstrates a complete FlowScript workflow that interacts with backend services through the TaskKernel runtime.

The workflow retrieves user data from an HTTP service, stores execution information in a database, publishes an event, and sends a notification after successful execution.

```flowscript
flow user_import {

    task fetch_users() {

        log("Fetching users from API")

        let response = http_get("/users")

        return response

    }

    step "Fetch Users" {

        let users = fetch_users()

        if users.status == 200 {

            db_insert("execution_logs", {
                "step": "Fetch Users",
                "status": "Success"
            })

            publish_event(
                "user.import.completed",
                users
            )

            notify("User import completed successfully")

        }
        else {

            notify("User import failed")

        }

    }

}
```

### Workflow Overview

The workflow above performs the following operations:

1. Defines a workflow named `user_import`.
2. Declares a reusable task named `fetch_users`.
3. Retrieves user data using an HTTP request.
4. Stores execution information in the database.
5. Publishes an event for downstream systems.
6. Sends a notification indicating the workflow result.

This example demonstrates the overall structure of a FlowScript program and illustrates how workflow logic is expressed using the language constructs defined throughout this specification.

---

## Conclusion

FlowScript Version 1.0 is a domain-specific scripting language designed for backend workflow automation within the TaskKernel platform. It provides a concise and readable way to define workflows that interact with backend services through a consistent set of language constructs and built-in operations.

This specification defines the syntax, execution model, and language features supported in FlowScript Version 1.0. It serves as the primary reference for the implementation of the FlowScript lexer, recursive descent parser, interpreter, and TaskKernel runtime.

As the implementation evolves, this document will be updated to reflect the capabilities of the language. The specification remains the authoritative source for the design and behavior of FlowScript.