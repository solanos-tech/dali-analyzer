# Backlog

Single source of truth for active iteration work.

## Status Values

- `todo`
- `in-progress`
- `blocked`
- `done-ready` (done in branch, pending merge)

## Active Items

| ID | Title | Priority | Status | Owner | Sprint/Iteration | Next Action | Last Updated |
|---|---|---|---|---|---|---|---|
| BKL-001 | Reorganize docs IA and root README | P1 | done-ready | team | 2026-05-06 | Merge PR and move to done-log | 2026-05-06 |
| BKL-002 | Introduce documentation governance for agent workflow | P1 | done-ready | team | 2026-05-06 | Merge PR and move to done-log | 2026-05-06 |
| BKL-003 | Expand test/module documentation depth | P1 | done-ready | team | 2026-05-06 | Merge PR and move to done-log | 2026-05-06 |
| BKL-004 | Validate links after docs path migration | P2 | in-progress | team | 2026-05-06 | Run path validation sweep | 2026-05-06 |
| BKL-005 | Standardize agent auto-PR and CI supervision loop | P1 | done-ready | team | 2026-05-06 | Merge PR #21 and move to done-log | 2026-05-06 |
| BKL-006 | Prepare release 0.9.4 (version bump + changelog) | P1 | done-ready | team | 2026-05-06 | Merge release PR, then run release publish from main | 2026-05-06 |
| BKL-007 | Apply AGPLv3 licensing plan (1:1) | P1 | done-ready | team | 2026-05-07 | Merge AGPL + version visibility PR and move to done-log | 2026-05-07 |
| BKL-008 | Redesign DALI Protocol Analyzer frontend | P1 | done-ready | prudek | 2026-06-10 | Merge UI redesign PR and monitor CI | 2026-06-10 |

## Refinement Notes

- Keep backlog rows short and action-oriented.
- Move completed rows to `done-log.md` during PR closeout.
- Keep no more than 10 active rows at one time; split large work into explicit tasks.

## BKL-007 Task Definition (Verbatim)

You are working in an existing open-source repository containing a Python backend and a TypeScript/React frontend.

Your task is to apply AGPLv3 licensing to the project in a clean, conventional, legally cautious way.

Goals:
1. Make the repository clearly licensed under GNU Affero General Public License v3.0.
2. Add the standard AGPLv3 license text.
3. Add clear README licensing information.
4. Add lightweight source-code license headers where appropriate.
5. Avoid modifying functional code behavior.

Required changes:

1. Add a root LICENSE file
- Create a file named exactly LICENSE in the repository root.
- Use the full, unmodified official text of GNU Affero General Public License v3.0.
- Use the official AGPLv3 text from the Free Software Foundation:
  https://www.gnu.org/licenses/agpl-3.0.txt
- Do not shorten, translate, paraphrase, or add custom clauses inside the AGPL text.

2. Add README license section
Add or update a section named "License" in README.md.

Suggested text:

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPLv3).

This means that you may use, study, modify, and redistribute this software under the terms of the AGPLv3. If you modify this software or make it available to users over a network, including as part of a hosted service, SaaS platform, internal web application, commissioning tool, diagnostic system, or product-integrated service, you must make the corresponding source code available under the same license.

For use cases where AGPLv3 obligations are not acceptable, including proprietary or closed-source commercial integrations, please contact the project owner to discuss a separate commercial license.

See the LICENSE file for the full license text.

3. Add source headers
Add short SPDX headers to source files where practical.

For Python files:

# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 prudek

For TypeScript / TSX / JavaScript files:

// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (C) 2026 prudek

Use the correct comment style for each file type.

Do not add headers to:
- generated files
- minified files
- lock files
- vendored third-party code
- build output
- node_modules
- virtual environments
- package manager caches
- binary files
- auto-generated API clients unless clearly maintained manually

4. Add package metadata if applicable
If package.json exists, add or update:

"license": "AGPL-3.0-or-later"

If pyproject.toml exists, add or update the license metadata according to the project's existing format. Prefer:

license = { text = "AGPL-3.0-or-later" }

or, if the project uses SPDX-style metadata:

license = "AGPL-3.0-or-later"

Do not break existing package configuration.

5. Optional but recommended: add LICENSE-FAQ.md
Create LICENSE-FAQ.md with a concise explanation:

- The project is AGPLv3-licensed.
- Commercial use is allowed only if AGPLv3 obligations are respected.
- If the software is modified and distributed, the modified source must be published.
- If the software is modified or used to provide a network-accessible service, corresponding source code must be made available to users of that service.
- Proprietary closed-source integrations require a separate commercial license from the copyright holder.
- This file is informational only and does not replace the LICENSE file.

6. Check dependency compatibility
Review dependency license metadata where available.
Flag potential incompatibilities, especially dependencies with:
- proprietary licenses
- non-commercial licenses
- Commons Clause
- SSPL
- unclear/custom licenses

Do not remove or replace dependencies without explicit approval. Report findings.

7. Preserve functionality
After applying changes:
- run formatting only if the project already has a formatter configured
- run available tests or at least basic lint/build checks if documented
- do not refactor unrelated code
- do not change runtime behavior

8. Final report
Return a concise report containing:
- files created
- files modified
- license identifier applied
- whether README was updated
- whether package metadata was updated
- whether source headers were added
- any files intentionally skipped
- any dependency license risks found
- tests/checks run and their result

Important legal constraints:
- Do not invent custom license terms.
- Do not add anti-corporate, non-commercial, or "no closed-source use" clauses to the AGPL text.
- Do not claim that AGPL forbids commercial use. It does not.
- State instead that proprietary/closed-source use may require a separate commercial license if the user cannot comply with AGPLv3 obligations.
- Keep the full AGPL text intact.
