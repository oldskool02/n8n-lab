# Bash Apprenticeship Notebook

This notebook records what I have learned while building the Operations Toolkit.

The goal is not to remember commands.

The goal is to understand software engineering.

---

# Philosophy

## Think before coding

Good software is designed before it is implemented.

Workflow:

Requirements

↓

Interface

↓

Architecture

↓

Implementation

↓

Testing

↓

Commit

---

## Bash is not the goal

Bash is simply the language used to express the design.

The real goal is learning:

- software architecture
- API design
- abstraction
- Unix philosophy
- engineering principles

---

# Engineering Principles

## Single Responsibility Principle

Every function should have one responsibility.

Example:

Good:

```
check_docker()
```

Not:

```
check_docker_and_restart_everything()
```

---

## Code to interfaces

Commands should not know implementation details.

Instead of:

```
printf ...
exit 1
```

Use:

```
fatal "Docker daemon is not running."
```

The framework handles implementation.

---

## Descriptive names

Prefer:

```
print_message()
```

Instead of:

```
print()
```

Code is read more often than it is written.

---

## Earn complexity

Do not build features before they are needed.

Examples:

Good:

Simple dispatcher

Later:

Logging

JSON output

Plugins

---

# Unix Philosophy

Bash orchestrates.

Unix programs perform the work.

Examples:

docker

jq

grep

awk

sed

The shell connects programs together.

---

# JSON

Never memorise JSON.

Instead:

Discover it.

Useful tools:

```
jq

jq '.'

jq 'keys'
```

The structure tells you how to query it.

---

# Pipelines

Everything is a pipeline.

```
stdout

↓

stdin

↓

next command
```

Programs should produce output suitable for another program to consume.

---

# Command Dispatcher

The dispatcher has one responsibility.

```
Determine command

↓

Load command

↓

Execute public interface
```

It does not contain business logic.

---

# Modules

Libraries are modules.

Commands are modules.

Only one executable exists.

```
bin/ops
```

Everything else is sourced.

---

# Public Interfaces

Every command exposes exactly one public function.

```
run_help()

run_version()

run_doctor()
```

Everything else should remain internal.

---

# APIs

Good APIs express intent.

Examples:

```
info()

success()

warn()

error()

fatal()
```

The caller describes intent.

The framework performs the work.

---

# Lessons Learned

## "$@"

Represents all remaining arguments.

Use:

```
run_version "$@"
```

to forward arguments unchanged.


## Golden Rule

When something goes wrong, ask:

**Who owns this responsibility?**

Do not ask:

"What command fixes it?"

Every problem belongs to a layer.

- Compose describes.
- Docker creates.
- Images provide software.
- Containers execute software.
- Volumes store persistent data.
- Networks transport traffic.
- Docker DNS resolves service names.
- Environment variables configure applications.
- Applications interpret their own configuration.

Understanding who owns the responsibility tells you where to troubleshoot.

---

## shift

Removes the first argument.

Example:

```
ops doctor --json
```

Before:

```
doctor
--json
```

After:

```
--json
```

The dispatcher owns the command.

The command owns everything after it.

---

## source

`source` loads a module into the current shell.

It does not start a new Bash process.

Because of this:

- modules do not need a shebang.
- modules inherit shell options.

---

# Git Workflow

Preferred workflow:

```
Discuss

↓

Design

↓

Implement

↓

Test

↓

Review

↓

Commit

↓

Push
```

Every commit should represent a complete, working feature.

# Naming Conventions
Names should describe what something is, not what you hope it becomes.
Good:

  message
  command
  container
  exit_code

Avoid:

  formatted_message   # unless it is guaranteed to be formatted

  valid_command        # unless it has already been validated

  running_container    # unless it is known to be running

Names should always be true.

# Notes
    Abstractions should return work, not perform unrelated work.


# String Literal Convention

Quote string literals passed as function arguments, even when Bash does not require it.

## Example:

  format_message "success" "$message"

  instead of:

  format_message success "$message"

## Rationale
  Clearly distinguishes string literals from variables.
  Improves readability during code reviews.
  Creates a consistent visual style.
  Avoids readers having to mentally apply Bash parsing rules.

## The Rule
  Single quotes for fixed literals.
  Double quotes for anything that requires expansion.
  Type	                  Quote           Style	Example
  Format strings	        Single quotes	  printf '%s\n' "$message"
  String literals (data)	Double quotes	  format_message "success" "$message"
  Variables	              Double quotes	  "$message"

## If a string can never change, make it look immutable.
  That means:
    Format strings → single quotes
    Regular expressions → single quotes
    Fixed shell patterns → single quotes


# Questions to ask when designing
  1. Who owns this information?
  2. Whose responsibility is this?
  3. Am I introducing hidden side effects?
  4. Does this function now do more than its name promises?
---

# Personal Goal

I am not trying to become someone who writes Bash scripts.

I am learning how to design and build maintainable software systems.

The language may change in the future.

The engineering principles will not.


# GIT
git status
git diff
git add .
git diff --staged
git commit -m "Refactor container checks to use a single Docker query"