# FlowScript Grammar Specification (Version 1.0)

**Language:** FlowScript

**Platform:** TaskKernel

**Current Version:** 1.0

**Status:** Draft

---

## 1. Introduction

FlowScript is a domain-specific scripting language (DSL) designed for defining backend automation workflows. It is the scripting language used by **TaskKernel**, a backend workflow automation platform that executes workflow scripts asynchronously against backend services and infrastructure.

Unlike general-purpose programming languages, FlowScript focuses on workflow orchestration rather than application development. It provides a concise syntax for describing common backend operations such as HTTP requests, database interactions, Redis messaging, notifications, delays, and retry policies without requiring developers to write repetitive orchestration code.

FlowScript is intentionally designed to remain small, readable, and predictable. Rather than supporting every feature found in a general-purpose programming language, it includes only the constructs necessary for building backend workflows, making scripts easier to write, understand, and maintain.

This document defines the syntax, language rules, supported constructs, and built-in functionality available in **FlowScript Version 1.0**.

### Design Goals

- Provide a simple and readable language for backend workflow automation.
- Reduce repetitive orchestration code commonly written in backend services.
- Offer built-in primitives for common backend operations.
- Keep the language intentionally small and focused.
- Produce deterministic and easy-to-understand workflow execution.

### Intended Use Cases

- Backend workflow automation
- API orchestration
- Database operations
- Event-driven pipelines
- Scheduled and background tasks

---

## 2. Language Overview

FlowScript is a statement-based, interpreted, domain-specific language designed for backend workflow automation. A FlowScript program consists of a sequence of statements that are executed from top to bottom by the TaskKernel runtime.

Each `.flow` file represents a single workflow. During execution, the runtime parses the script, validates its syntax, and executes each statement sequentially while maintaining execution state, variables, and runtime logs.

Unlike general-purpose programming languages, FlowScript provides built-in primitives for common backend operations such as HTTP requests, database interactions, Redis messaging, notifications, delays, and retry mechanisms. These operations are treated as first-class language constructs, allowing developers to describe complex backend workflows using concise scripts.

### Characteristics

- Interpreted language (no compilation step)
- Statement-based execution
- Domain-specific language (DSL)
- Backend workflow oriented
- Built-in backend operations
- Strong focus on readability and simplicity
- Designed to execute within the TaskKernel runtime

---