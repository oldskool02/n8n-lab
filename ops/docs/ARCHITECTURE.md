# Operations Toolkit Architecture

## Purpose

The Operations Toolkit (`ops`) is a modular command-line application designed to simplify the administration of the n8n-lab environment.

The project follows a framework-first architecture. Commands express intent while shared framework services implement common behaviour.

---

# Design Principles

The project follows these principles:

1. Interface before implementation.
2. Single Responsibility Principle.
3. Code to interfaces, not implementations.
4. Prefer descriptive names.
5. Prefer convention over innovation.
6. Earn complexity.
7. Bash orchestrates. Unix tools perform the work.

---

# High-Level Architecture

```
                User
                  │
                  ▼
             bin/ops
                  │
                  ▼
          Command Dispatcher
                  │
                  ▼
          Command Module
                  │
                  ▼
         Framework Services
                  │
                  ▼
          System / Docker
```

---

# Directory Structure

```
ops/

├── bin/
│   └── ops
│
├── commands/
│   ├── help.sh
│   ├── version.sh
│   └── doctor.sh
│
├── lib/
│   ├── common.sh
│   ├── config.sh
│   ├── docker.sh
│   └── system.sh
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── ROADMAP.md
│
└── VERSION
```

---

# Responsibilities

## bin/ops

The dispatcher.

Responsibilities:

- Initialise the application.
- Parse arguments.
- Locate the requested command.
- Load the command module.
- Invoke the command's public interface.

The dispatcher contains no business logic.

---

## Command Modules

Each command module exposes exactly one public function.

Example:

```
run_help()
run_version()
run_doctor()
```

Command modules should:

- implement command-specific behaviour.
- call framework services.
- not perform global initialisation.

---

## Framework Services

Framework services live inside `lib/`.

They provide reusable functionality shared by every command.

Examples include:

- user interaction
- validation
- Docker operations
- system checks
- configuration

---

## Common Framework

`common.sh` provides framework-level services.

Current responsibilities include:

- shared helper functions

Future responsibilities:

- print_message()
- info()
- success()
- warn()
- error()
- fatal()
- validation services
- logging
- output formatting

---

# Command Lifecycle

Every command should follow the same lifecycle.

```
Validate input
        │
        ▼
Validate environment
        │
        ▼
Execute command
        │
        ▼
Present results
        │
        ▼
Exit
```

---

# Public Interfaces

Framework services expose stable interfaces.

Commands should call framework functions instead of implementing their own behaviour.

Example:

```
error "Docker daemon is not running."

fatal "Unable to continue." "$EXIT_GENERAL_ERROR"
```

Commands express intent.

The framework determines presentation.

---

# Future Architecture

Planned framework capabilities include:

- consistent output formatting
- structured logging
- JSON output
- verbosity levels
- colour support
- standard exit codes
- plugin-style command discovery

These features should be introduced only when justified by project requirements.

The project follows the principle:

> Earn complexity.

# The framework gives us:
  error()
  fatal()

## The framework doesn't know when to use them.
  The doctor command decides.

## For doctor, the rule is:
  Docker unavailable → fatal()
  Container unhealthy → error()
  Missing optional service → maybe warn()
  Healthy service → success()