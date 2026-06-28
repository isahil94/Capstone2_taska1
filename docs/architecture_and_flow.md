# Architecture and Execution Flow (code-grounded)

This document describes the actual architecture and request/processing flow implemented in the repository (based on code), not the conceptual AI_CONTEXT.md.

## High-level components

- **API / Presentation**: FastAPI application created in `backend/app/bootstrap.py` and launched from `backend/main.py`.
  - Routes are implemented in `backend/app/presentation/api/routes/` (e.g. `system.py`, `repository.py`).
  - HTTP middleware and exception handlers are registered in `backend/app/presentation/http/`.

- **Dependency Injection Container**: `backend/app/container.py` wires service factories, repositories, and infrastructure (database engine / session factory).

- **Application Services (deterministic logic)**: Located in `backend/app/application/services/`.
  - `ParserService` — Tree-sitter parsing and symbol extraction (`parser_service.py`).
  - `RepositoryIntelligenceService` — graph building (dependency, call, class, architecture) (`repository_intelligence_service.py`).
  - `RepositoryService` — clone, update, validate repository, read .gitignore (`repository_service.py`).
  - `SystemService` — health and version endpoints (`system_service.py`).

- **Repository Interfaces + Implementations**: Contracts in `backend/app/application/repositories/` and SQLAlchemy-backed implementations in `backend/app/infrastructure/persistence/repositories/`.

- **Persistence / Infrastructure**: SQLAlchemy models and session factory under `backend/app/infrastructure/persistence/` and wired in the DI container.

- **Docs / Agents / Skills (design artifacts)**: `.github/AGENTS.md` and `.github/skills/` document agent/skill roles; these are documentation artifacts and not a runtime agent orchestrator.


## Runtime application startup

1. `backend/main.py` imports and calls `create_app()` from `backend/app/bootstrap.py` and runs Uvicorn.
2. `create_app()` constructs the DI `Container`, configures logging, wires dependencies, and registers a lifespan context that initializes container resources and stores the container and settings on `application.state`.
3. Middleware and exception handlers are registered; routers for `system` and `repositories` are included.


## Typical request flows

1. Clone repository (HTTP POST `/repositories/clone`)
   - Route: `backend/app/presentation/api/routes/repository.py:clone_repository`
   - Calls `RepositoryService.clone_repository` which runs `git clone` and persists metadata via the metadata repository implementation.

2. Parse repository (HTTP POST `/repositories/parse`)
   - Route: `backend/app/presentation/api/routes/repository.py:parse_repository`
   - Calls `ParserService.parse_repository` which:
     - Walks the repository files (skips configured dirs)
     - Uses Tree-sitter to parse files and extract symbols
     - Persists parser results via `ParserResultRepository.upsert_many` (SQLAlchemy implementation: `infrastructure/persistence/repositories/parser_result_repository.py`).

3. Build repository intelligence graphs (HTTP POST `/repositories/intelligence/graphs`)
   - Route: `backend/app/presentation/api/routes/repository.py:build_repository_graphs`
   - Calls `RepositoryIntelligenceService.build_graphs` which:
     - Reads persisted parser results
     - Constructs import, dependency, call, class, and architecture graphs deterministically
     - Persists graph snapshots via `RepositoryGraphRepository` implementation


## Middleware, logging, and error handling

- Request context middleware with `X-Request-ID`, timing, and structured logging: `backend/app/presentation/http/middleware.py`.
- Standardized HTTP exception handling mapped from `AppError` and validation errors: `backend/app/presentation/http/exception_handlers.py`.


## Where agents / skills appear vs. where logic runs

- Agents and skills are documented as design-level concepts in `.github/AGENTS.md` and `.github/skills/`. They describe how higher-level orchestrations should invoke the deterministic services.
- The running code implements the deterministic services, persistence layers, and API — actual runtime orchestration is performed by HTTP routes and DI wiring, not by separate agent processes in this codebase.


## Key files (start here)

- App factory / entry: [backend/main.py](backend/main.py)
- App boot & DI: [backend/app/bootstrap.py](backend/app/bootstrap.py)
- DI container: [backend/app/container.py](backend/app/container.py)
- API routes: [backend/app/presentation/api/routes/repository.py](backend/app/presentation/api/routes/repository.py) and [backend/app/presentation/api/routes/system.py](backend/app/presentation/api/routes/system.py)
- Services: [backend/app/application/services/parser_service.py](backend/app/application/services/parser_service.py), [backend/app/application/services/repository_intelligence_service.py](backend/app/application/services/repository_intelligence_service.py)
- Persistence implementations: [backend/app/infrastructure/persistence/repositories/parser_result_repository.py](backend/app/infrastructure/persistence/repositories/parser_result_repository.py)
- Middleware and errors: [backend/app/presentation/http/middleware.py](backend/app/presentation/http/middleware.py), [backend/app/presentation/http/exception_handlers.py](backend/app/presentation/http/exception_handlers.py)
- Design docs for agents/skills: [.github/AGENTS.md](.github/AGENTS.md), [.github/skills/README.md](.github/skills/README.md)


## Quick sequence diagram (request flow)

Client -> FastAPI router -> Route handler -> Service (business logic) -> Repository impl (persistence) -> DB


## Next steps I can take for you

- Expand this doc with diagrams (Mermaid) showing the clone->parse->build flow.
- Extract service method signatures and a dependency graph of modules.
- Generate a visual architecture diagram for the frontend + backend interaction.

If you want diagrams or a deeper mapping (file-by-file), tell me which output you prefer and I'll generate it next.
