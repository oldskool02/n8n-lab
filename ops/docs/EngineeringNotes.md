# Engineering Notes(living section)
Docker Compose is a blueprint, not a script.
A service is a specialist with one primary responsibility.
PostgreSQL is the system's long-term memory.
Redis is the system's short-term working memory.
Services communicate with each other instead of trying to do everything themselves.

Describe the logical system. Let the platform manage the physical implementation.
The Compose author defines the logical architecture (the service names). Docker implements the physical network (the IP addresses).
Describe the logical system. Let the platform manage the physical implementation.

Depend on stable contracts, not changing implementation details.
Good: DB_POSTGRESDB_HOST=postgres
Bad: DB_POSTGRESDB_HOST=172.18.0.2

| Department   | Responsibility                               |
| ------------ | -------------------------------------------- |
| n8n          | Operations Manager                           |
| PostgreSQL   | Records Department                           |
| Redis        | Reception Desk (fast, temporary information) |
| Cloudflared  | Front Gate                                   |
| Ollama       | AI Consultant                                |
| Chat Backend | Customer Service                             |
| Portainer    | IT Administrator                             |
| Netdata      | Monitoring & Health                          |

The desired state describes what must exist, not the steps required to create it.

| Feature       | Responsibility            | Active When?               |
| ------------- | ------------------------- | -------------------------- |
| `depends_on`  | Startup orchestration     | Startup only               |
| `healthcheck` | Report application health | Continuously while running |
| `restart`     | Recover from process exit | Runtime                    |


# Architectural Principle #1

Every component in a system must have one clear responsibility.

If an existing component already fulfills that responsibility well, introducing another component adds unnecessary complexity.

We don't add anything to the architecture until
1. we can explain why it exists,
2. what responsibility it owns, and
3. what would happen if it disappeared

## Docker Compose

A Docker Compose file is a description of the system I want Docker to build.

It is declarative, not imperative.

A Compose file is a declarative specification of the desired state of a system.

Docker Compose does not build containers itself. It describes the desired system to Docker Engine, which creates and manages the containers.

Configuration belongs in Git. Secrets do not.

# Secrets
## Golden Rule

Configuration tells the application **what** to connect to.

Secrets prove the application is **allowed** to connect.

Any piece of information that proves identity or grants access is a secret.

Configuration tells a system what to do.

Secrets prove that the system is allowed to do it.

The `services:` section is simply a grouping that says:

> "Everything below here is a service that forms part of this system."

It is not a command. It is a heading.

## Structure of the Compose file
A Compose file is structured data.
services: tells Docker where the service definitions begin.

Filing Cabinet
│
├── Services
│     ├── PostgreSQL
│     ├── Redis
│     └── n8n
│
├── Networks
│
└── Volumes

### Keywords vs Names

Not every word in a Docker Compose file has the same meaning.

Some words are defined by the Compose specification (for example `services`, `volumes`, `networks`, and `secrets`). These are keywords and cannot be renamed.

Other words, such as `postgres`, `redis`, and `n8n`, are service names that I choose. They identify my services within the project.

A service name is not the software itself. The software is defined by the `image` (or sometimes by a `build` section).

## Service Name vs Image

A service has two separate identities.

The **service name** identifies the service within the Docker Compose project. Other services use this name to communicate with it.

The **image** tells Docker Engine what software to run inside the container.

These serve different purposes:

- **Service name** → Who am I?
- **Image** → What software do I run?

Changing the image (for example, upgrading PostgreSQL from version 16 to 17) does not require changing the service name. Other services continue communicating with the same service name, making the implementation replaceable while the interface remains stable.

## Images, Containers and Volumes

These are three different concepts with different responsibilities.

- **Image** – A read-only package containing the application and everything needed to run it. It answers the question: *"What software should Docker run?"*

- **Container** – A running instance created from an image. It is the executing application.

- **Volume** – Persistent storage used by a container. It stores data that must survive even if the container is removed and recreated.

Relationship:

Image → creates → Container → uses → Volume

Each component has a single responsibility.

# Architecture and Configuration

Architecture decides what should happen.

Configuration tells the software how to make it happen.

Examples:

Architecture: We need a relational database.
Configuration: DB_TYPE=postgresdb
Architecture: We need persistent storage.
Configuration: n8n_data:/home/node/.n8n
Architecture: We don't expose n8n directly to the Internet.
Configuration: 127.0.0.1:5678:5678 and Cloudflared.

That distinction is subtle, but it's one of the things that separates someone who can edit a configuration file from someone who can design a system.

| Architecture | Configuration  |
| ------------ | -------------- |
| Why?         | How?           |
| Intent       | Implementation |
| Design       | Settings       |
| Requirements | Values         |
| Decisions    | Parameters     |
| ------------ | ---------------|

Architecture defines what the system must achieve.

Configuration tells the software how to achieve it.

Architecture is the intent.

Configuration is the implementation.
