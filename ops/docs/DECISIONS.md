# Architecture Decisions

This document records significant architectural decisions made during the development of the Operations Toolkit.

Each decision captures the reasoning behind the design so that future contributors understand not only *what* was decided, but *why*.

---

## ADR-001

### Title

Single Executable Entry Point

### Status

Accepted

### Decision

The project will have exactly one executable entry point.

```
bin/
└── ops
```

All command modules and libraries are sourced by the dispatcher.

### Rationale

A single entry point provides:

- consistent application initialisation
- centralised argument parsing
- simplified testing
- a stable public interface
- consistent command execution

---

## ADR-002

### Title

Command Module Interface

### Status

Accepted

### Decision

Every command module exposes exactly one public function.

Examples:

```bash
run_help()
run_version()
run_doctor()
```

The dispatcher dynamically invokes the command by calling the corresponding public function.

### Rationale

This creates a clear contract between the dispatcher and command modules while allowing internal implementation to evolve without affecting the dispatcher.

---

## ADR-003

### Title

Framework API Design

### Status

Accepted

### Decision

The framework exposes the following public functions:

```text
print_message()

info()
success()
warn()
error()
fatal()
```

Commands express intent.

Framework services implement behaviour.

### Responsibilities

| Function | Responsibility |
|----------|----------------|
| print_message() | Print the supplied message exactly as received. |
| info() | Format an informational message. |
| success() | Format a success message. |
| warn() | Format a warning message. |
| error() | Format an error message. |
| fatal() | Display an error and terminate execution. |

### Rationale

This follows the Single Responsibility Principle and keeps presentation separate from command logic.

---

## ADR-004

### Title

Framework Exit Codes

### Status

Accepted

### Decision

The framework defines standard exit codes grouped by failure category.

```bash
EXIT_SUCCESS=0

EXIT_GENERAL_ERROR=1
EXIT_INVALID_ARGUMENT=2

EXIT_DEPENDENCY_MISSING=10
EXIT_CONFIGURATION_ERROR=11
EXIT_ENVIRONMENT_ERROR=12

EXIT_NOT_FOUND=20
EXIT_PERMISSION_DENIED=21

EXIT_OPERATION_FAILED=30
```

Command modules use symbolic constants instead of numeric values.

Example:

```bash
fatal "Docker daemon is not running." "$EXIT_ENVIRONMENT_ERROR"
```

### Rationale

Exit codes communicate failure categories to automation.

Error messages communicate specific causes to humans.

---

## ADR-005

### Title

Message Formatting Standard

### Status

Accepted

### Decision

The framework will use descriptive message prefixes.

Examples:

```text
Info: Checking Docker...

Success: Docker daemon is running.

Warning: Docker Compose is not installed.

Error: Docker daemon is not running.
```

Higher-level framework functions format the message before passing it to `print_message()`.

Example:

```bash
success "Docker daemon is running."

↓

print_message "Success: Docker daemon is running."
```

`print_message()` remains completely generic.

### Rationale

This design keeps responsibilities clearly separated while producing consistent, professional output across the application.

The framework can later introduce colours, timestamps or structured output without changing the public API.

## ADR-006
### Title

Framework Contract

### Status

Accepted

### Decision

Framework functions assume they are called correctly.

Commands are responsible for validating all user input before invoking framework services.

Framework functions do not validate programmer errors.

### Rationale

The framework is an internal implementation detail, not a public interface exposed to users.

Separating validation from framework behaviour keeps responsibilities clear and avoids unnecessary defensive programming.


## ADR-007 – Message Formatting Layer

### Decision

Introduce an internal format_message() function to eliminate duplicated formatting logic.

### Rationale

Message formatting is a single responsibility shared by multiple public API functions.

### Centralising formatting:

removes duplication,
improves consistency,
simplifies maintenance,
preserves the public API,
follows the Single Responsibility Principle.

----------------------------------------------------------------------------------------------------

# Guiding Principles

Every architectural decision should support these principles.

- Interface before implementation.
- Single Responsibility Principle.
- Commands express intent.
- Framework services implement behaviour.
- Prefer descriptive names.
- Prefer convention over innovation.
- Earn complexity.
- Hide implementation behind stable interfaces.