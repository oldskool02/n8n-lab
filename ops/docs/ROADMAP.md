# Operations Toolkit Roadmap

The roadmap describes the planned evolution of the Operations Toolkit.

Features are grouped into milestones rather than dates.

A feature should only move into development when the current milestone has been completed and tested.

---

# Project Vision

The Operations Toolkit should become a modular administration framework for the entire n8n-lab environment.

The toolkit should:

- simplify administration
- automate repetitive tasks
- provide consistent diagnostics
- expose a clean command-line interface
- be easy to extend with new commands

The project follows the principle:

> Earn complexity.

---

# Current Status

## Version

2.3.0

## Completed

✔ Modular command dispatcher

✔ Command modules

✔ Framework architecture

✔ Docker subsystem

✔ System diagnostics

✔ Version command

✔ Help command

✔ Doctor command

---

# Milestone 1
## Foundation

Status: Complete

### Goals

- Single executable entry point
- Modular commands
- Shared libraries
- Version management
- System diagnostics
- Docker diagnostics

---

# Milestone 2
## Framework

Status: In Progress

### Objectives

Build the common framework used by every command.

### Planned Features

- print_message()
- info()
- success()
- warn()
- error()
- fatal()

- Standard exit codes

- Command validation

- Framework error handling

- Consistent output formatting

### Success Criteria

Every command uses framework services rather than implementing its own output.

---

# Milestone 3
## Command Discovery

### Planned Features

Automatic discovery of commands.

Instead of maintaining command lists manually:

```
commands/
    backup.sh
    doctor.sh
    help.sh
```

The framework should discover available commands automatically.

### Benefits

- Less duplication
- Easier maintenance
- Self-documenting CLI

---

# Milestone 4
## Docker Management

### Planned Commands

```
ops ps

ops logs

ops restart

ops start

ops stop

ops update

ops health
```

### Future Features

Container filtering

Health reporting

Restart policies

Version detection

Rolling updates

---

# Milestone 5
## Backup & Recovery

### Planned Commands

```
ops backup

ops restore

ops verify

ops snapshot
```

### Features

PostgreSQL backups

Docker volume backups

Configuration backups

Restore verification

Retention policies

Automatic cleanup

---

# Milestone 6
## Deployment

### Planned Commands

```
ops deploy

ops rollback

ops upgrade
```

### Features

Compose validation

Version upgrades

Automatic rollback

Health verification

Deployment reports

---

# Milestone 7
## Monitoring

### Planned Commands

```
ops monitor

ops status

ops metrics
```

### Features

Resource monitoring

Container health

Disk usage

Memory usage

CPU usage

Alerting

---

# Milestone 8
## Output Improvements

### Features

Colour output

JSON output

Verbose mode

Quiet mode

Progress indicators

Tables

Interactive prompts

---

# Milestone 9
## Configuration

### Features

Configuration files

Environment profiles

Development mode

Production mode

Custom settings

---

# Milestone 10
## Plugin Architecture

Long-term goal.

Allow third-party command modules.

Example:

```
commands/

    backup.sh

    doctor.sh

plugins/

    my-company.sh

    monitoring.sh
```

The dispatcher should discover plugins automatically.

---

# Technical Debt

The following improvements are intentionally postponed.

## Logging

Structured logging

Log files

Debug logging

Log rotation

---

## Testing

Unit testing

Integration testing

ShellCheck

CI pipeline

GitHub Actions

---

## Documentation

Expand user guide

Examples

Tutorials

Architecture diagrams

API reference

---

# Ideas Parking Lot

Ideas that should not interrupt the current sprint.

- Interactive menu mode
- Shell auto-completion
- Remote server management
- SSH support
- Kubernetes support
- Podman support
- Container templates
- Health dashboards
- Performance benchmarking
- Automatic updates

# Developer Environment
  VS Code Server cleanup
  Detect orphaned VS Code Server versions
  Check Docker version
  Check Git version
  Check Python version
  Check available disk space
  Check backup age
---

# Guiding Principles

Before implementing a feature ask:

1. Does it solve a real problem?

2. Does it belong in this project?

3. Can the framework already support it?

4. Can it be implemented simply?

5. Have we earned the complexity?

If the answer to these questions is "No", the feature belongs in the roadmap—not in the current sprint.


# Sprint 3 – Framework Foundation
Implement the common messaging framework and standard exit codes that will serve as the foundation for all current and future commands.


# Completed Milestones

## v2.1
- Modular command dispatcher
- Command modules

## v2.2
- Docker subsystem
- Doctor command

## v2.3(In progress)
- Help command
- Public command interfaces
- Framework architecture