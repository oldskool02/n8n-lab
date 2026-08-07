# The n8n-Lab Architecture Project

> **Mission Statement**
>
> Build an infrastructure that is not only reliable and maintainable, but one that is fully understood. Every decision must be deliberate, every component must have a purpose, and every change must be justified.

---

# Guiding Principles

## Rule 1 — Understand First. Change Second.

We never change anything until we understand:

- What it does.
- Why it exists.
- What problem it solves.
- The consequences of changing or removing it.

If we don't understand it, we stop and learn.

---

## Rule 2 — Every Line Must Have a Reason

Every important line in the repository should be able to answer four questions:

1. What does it do?
2. Why is it here?
3. What problem does it solve?
4. What happens if I remove it?

If these questions cannot be answered, the line should not remain in the project.

---

## Rule 3 — No Copy-and-Paste Engineering

Nothing enters the project simply because it appeared in a tutorial, Stack Overflow answer, or documentation.

Every configuration option, command, environment variable, volume, network, secret, and service must be understood before it becomes part of the system.

---

## Rule 4 — Simplicity Wins

Every improvement should make the system:

- easier to understand,
- easier to maintain,
- easier to troubleshoot,
- easier to recover.

We avoid unnecessary complexity.

Simple systems are reliable systems.

---

## Rule 5 — Development Before Production

The Home Server is the laboratory.

The VPS is production.

All architectural changes are designed, tested and understood on the Home Server before being deployed to the VPS.

Production is never used for experimentation.

---

## Rule 6 — Git Is Our History

Git records the evolution of the project.

We avoid keeping:

- `.bak`
- `.old`
- `Copy`
- dated copies

unless there is a specific reason that Git cannot solve.

When Git is being used correctly, the repository remains clean and the history remains available.

---

## Rule 7 — One Change at a Time

Every change should be:

1. Planned.
2. Implemented.
3. Tested.
4. Committed to Git.

Avoid making multiple unrelated changes simultaneously.

If something breaks, we should immediately know where to investigate.

---

## Rule 8 — Design Before Implementation

Before editing files, we first understand the architecture.

Questions come before commands.

Design comes before implementation.

Understanding comes before configuration.

---

# Learning Philosophy

Success is **not** measured by whether the server works.

Success is measured by whether I can explain:

- why every service exists,
- why every volume exists,
- why every network exists,
- why every secret exists,
- why every configuration value exists.

If I cannot explain it, I do not yet understand it.

---

# Definition of Done

A task is only complete when I can confidently answer:

- What does it do?
- Why does it exist?
- How does it work?
- What would happen if I removed it?
- Could I rebuild it from scratch?

If the answer to any of these is **No**, then the task is not yet finished.

---

# Project Goal

Build an infrastructure that I fully understand.

Not one that merely works.

Not one that was copied.

Not one that depends on memory.

But one that I can confidently:

- explain,
- maintain,
- troubleshoot,
- recover,
- improve,
- and rebuild from scratch.

---

> **Project Motto**
>
> **Understand first. Build second.**
>
> Every line should have a purpose.
> Every decision should have a reason.
> Every system should be understandable.


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

| Section        | Responsibility                              |
| -------------- | ------------------------------------------- |
| `services:`    | Defines the system.                         |
| `image:`       | Specifies the software template.            |
| `restart:`     | Describes the desired running state.        |
| `environment:` | Configures the application.                 |
| `secrets:`     | Provides confidential information securely. |
| `volumes:`     | Persists data outside the container.        |
| `networks:`    | Allows services to communicate.             |
| `ports:`       | Exposes selected services to the host.      |
| `depends_on:`  | Expresses startup dependencies.             |

# Golden Rule

A docker-compose.yml file does not describe **how** to build a system.

It describes **what the finished system should look like**.

Docker Engine is responsible for making reality match that description.
