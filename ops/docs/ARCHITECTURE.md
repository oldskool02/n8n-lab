# Operations Toolkit Architecture


# Engineering Philosophy

The Operations Toolkit is a Compose-aware application.

The Operations Toolkit is not a collection of Bash scripts.

It is a software system implemented in Bash.

The architecture is designed around responsibilities rather than technologies.

Commands express intent.

Framework components perform work.

External tools own their respective domains.

The shell orchestrates the system.

## Purpose

The Operations Toolkit (`ops`) is a modular command-line application designed to simplify the administration of the n8n-lab environment.

The project follows a framework-first architecture. Commands express intent while shared framework Components implement common behaviour.

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
         Framework Components
                  │
                  ▼
              Adaptors
                  │
                  ▼
               Docker
                  │
                  ▼
                Linux
                  │
                  ▼
                 Git

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
- call framework Components.
- not perform global initialisation.

---

## Framework Components

Framework Components live inside `lib/`.

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

## Commands express intent, not implementation.

Every command should follow the same lifecycle.

```
Understand Request
        │
        ▼
Collect Data
        │
        ▼
Build Model
        │
        ▼
Present Model
        │
        ▼
Return exit status
```

---

# Public Interfaces

Framework Components expose stable interfaces.

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

# Models
## Domain Model

  The framework defines its own models.

  Models represent reality.

  They do not expose vendor-specific structures.

  Example:
  Docker JSON

  ↓

  ServiceStatus

  ↓

  Presentation

The remainder of the framework should depend on the model rather than Docker's JSON.

# External Contracts
  The framework depends on external contracts.

  Examples:

    - Docker CLI
    - Docker JSON output
    - jq
    - Git

  Changes to external contracts should be isolated to adapter modules.

  Framework commands should not depend directly on vendor-specific implementations.

## The Framework Owns the Public Model

  External tools expose their own data structures.

  The framework converts those structures into its own domain models.

  These domain models form the public contract of the framework.

  Presentation layers and external consumers depend on the framework's models, not on vendor-specific data.



# Presentation Framework

## Responsibility

  - Formatting messages
  - Printing messages
  - Headers
  - Tables
  - Colours

## Owned by:

  lib/print.sh


## Ownership
print.sh
---------
Owns:
- Message formatting
- Message output
- Headers
- Tables
- Terminal presentation

docker.sh
----------
Owns:
- Docker CLI
- Docker JSON
- ServiceStatus construction

system.sh
----------
Owns:
- Prerequisite verification
- System capability checks