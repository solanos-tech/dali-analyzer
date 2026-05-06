# Documentation

This repository uses an agent-oriented documentation layout.

## Structure

- [adr/](adr/) - architecture and decision records
- [agent/](agent/) - operating guidance for AI and human contributors
- [ci-cd.md](ci-cd.md) - end-to-end CI/CD pipeline and policy map
- [test/](test/) - testing strategy, commands, and quality gates
- [tasks/](tasks/) - task registry, roadmap, and delivery tracking
- [modules/](modules/) - module-level reference docs

## Maintenance Rules

- Keep all documentation in English.
- Update `docs/tasks/projects.md` when project status changes.
- Update `docs/tasks/backlog.md` and `docs/tasks/done-log.md` for each material PR.
- Add iteration notes in `docs/tasks/iterations/`.
- Add new decisions as ADR files in `docs/adr/`.
- Update `CHANGELOG.md` for material process or product changes.
- Keep operational traces in `docs/agent/knowledge-log.md` and `docs/agent/decision-log.md`.
