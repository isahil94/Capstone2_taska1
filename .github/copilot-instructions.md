# GitHub Copilot Instructions

## Project Context
Before making any changes, read **AI_CONTEXT.md**.
`AI_CONTEXT.md` is the single source of truth for:
* Project architecture
* Components
* Services, tools, skills, and agents
* Technology stack
* Workflows
* Development phases
* Design decisions
Do not duplicate or redefine its contents.

---

## Development Rules
Before implementing any feature:
1. Identify the correct component.
2. Explain why the implementation belongs there.
3. Identify the files that need to change.
4. Modify only what is required.
5. Avoid unrelated refactoring.

---

## Implementation Guidelines
Always:
* Follow the architecture defined in `AI_CONTEXT.md`
* Follow the existing project structure
* Write clean, maintainable code
* Use type hints
* Handle errors appropriately
* Keep functions focused and reusable
* Prefer simple solutions over unnecessary abstraction

Do not:
* Introduce new frameworks without approval
* Redesign existing architecture
* Create new services, tools, skills, or agents without approval
* Move responsibilities between architectural layers without justification

---

## Testing
Every functional change must include appropriate validation.
Use:
* Unit tests for business logic
* API tests for endpoints
* LangGraph workflow tests when workflows change

---

## AI Development Guidelines
Prefer:
* Repository Intelligence
* Retrieval
* Context filtering
* Citations
* Deterministic preprocessing
Avoid:
* Repository-wide prompts
* Sending unnecessary context to LLMs
* Unsupported assumptions
* Hallucinated repository information

---

## Dependencies
Before adding a dependency, explain:
* Why it is required
* What problem it solves
* Alternatives considered
Prefer existing project dependencies whenever possible.

---

## Security
Never commit:
* Secrets
* API keys
* Passwords
* Tokens
Use environment variables for configuration.

---

## Documentation
Update documentation whenever architecture or behavior changes.
Keep `AI_CONTEXT.md` synchronized with implementation.

---

## Git
Use conventional commit prefixes:
* feat:
* fix:
* refactor:
* docs:
* test:
* chore:

---

## Completion Checklist
Before finishing any task, verify:
* [ ] AI_CONTEXT.md followed
* [ ] Correct architectural component updated
* [ ] No unnecessary architecture changes
* [ ] Appropriate tests added
* [ ] No duplicate logic introduced
* [ ] Documentation updated if required