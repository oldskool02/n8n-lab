# DESIGN.md

This document records the architectural decisions, coding standards, and behavioural contracts of the project.

---

# Design Principles

These principles guide architectural and implementation decisions throughout the project. When making design choices, prefer the solution that best aligns with these principles.

- **KISS (Keep It Simple, Stupid)**
  Prefer the simplest solution that clearly expresses its purpose.

- **One Responsibility Per Function**
  Each function should do one thing and do it well.

- **Commands Express Intent**
  Commands should describe *what* they do, not *how* they do it.

- **Evidence Before Action**
  Gather facts before making decisions or reporting results.

- **Incremental Refactoring**
  Improve the system through small, continuous changes rather than large rewrites.

- **Consistency Over Personal Preference**
  Once a project standard has been adopted, follow it consistently.

- **Prefer Named Concepts Over Repeated Implementation**
  When the same implementation appears repeatedly, consider introducing a higher-level abstraction that represents the concept.

- **Every Responsibility Has an Owner**
  Every responsibility belongs to a specific function, module, or command. Ownership should always be clear.

## Naming

Function and variable names should describe their responsibility or the concept they represent rather than the underlying implementation.

Prefer project terminology over technology-specific terminology where it accurately expresses the abstraction.

Examples:

```text
show_service_status()    ✓
check_container()        ✗

service_status           ✓
container                ✗
```

---

# Function Specifications

Function specifications describe the purpose, responsibilities, contracts and side effects of individual functions.

## Function: `check_docker_cli()`

### Purpose

Verify that the Docker CLI is installed and operational.

### Responsibilities

- Verify the Docker CLI exists.
- Verify the Docker CLI is executable.
- Display the Docker CLI version.

### Returns

- `EXIT_SUCCESS`
- `EXIT_ERROR`

### Side Effects

- Reports status to the user.
- Displays the Docker CLI version on success.

### Does NOT

- Start Docker.
- Install Docker.
- Modify system configuration.

---

# Command Specifications

Command specifications define the mission and responsibilities of top-level commands.

## Command: `doctor`

### Mission

Evaluate the health of the development environment.

### Responsibilities

- Verify prerequisites.
- Verify Docker.
- Verify managed services.
- Report issues requiring attention.

### Does NOT

- Repair problems automatically.
- Update software.
- Change configuration.

---

# Coding Standards

These standards exist to improve readability, maintainability, and consistency across the project. Once adopted, they should be applied consistently.

---

## Functions

Functions use `lowercase_snake_case` with the opening brace on the same line.

```bash
check_docker() {
    ...
}
```

---

## Local Variables

Local variables use `lowercase_snake_case`.

```bash
local service
local state
local health
local image
```

Local variables should be declared at the beginning of the function where practical.

Assign positional parameters to meaningful local variables immediately.

```bash
section() {
    local heading="$1"

    ...
}
```

Avoid using `$1`, `$2`, etc. throughout the function body.

---

## Global Constants

Global constants use `UPPER_SNAKE_CASE`.

```bash
readonly PROJECT_ROOT="/opt/ops"
readonly VERSION="1.0.0"
readonly DEFAULT_TIMEOUT=30
```

Constants should be declared `readonly` whenever possible.

---

## Environment Variables

Standard operating system environment variables retain their original uppercase names.

Examples:

```text
HOME
PATH
USER
SHELL
```

Do not rename or wrap standard environment variables simply to match project conventions.

---

# Consistency

Consistency is preferred over individual coding style.

Once a project standard has been adopted, it should be followed throughout the codebase. Any future changes to the coding standard should be deliberate architectural decisions and applied consistently.