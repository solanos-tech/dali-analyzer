# Documentation

This repository uses an agent-oriented documentation layout.

## Structure

- [adr/](adr/) - architecture and decision records
- [agent/](agent/) - operating guidance for AI and human contributors
- [cicd/](cicd/) - end-to-end CI/CD pipeline and policy map
- [test/](test/) - testing strategy, commands, and quality gates
- [tasks/](tasks/) - backlog, planning, templates, and iteration notes
- [modules/](modules/) - module-level reference docs
- [standards/](standards/) - protocol and sample stream references

## Maintenance Rules

- Keep all documentation in English.
- Update `docs/tasks/backlog.md` for active tasks in every iteration.
- Move completed items to `docs/tasks/done-log.md`.
- Add short iteration notes under `docs/tasks/iterations/`.
- Add new decisions as ADR files in `docs/adr/`.
- Update `CHANGELOG.md` for material process or product changes.
- Keep operational traces in `docs/agent/knowledge-log.md` and `docs/agent/decision-log.md`.
