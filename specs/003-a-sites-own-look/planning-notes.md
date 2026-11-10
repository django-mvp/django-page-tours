# Planning notes — FS-003 A site's own look for its tours

Suggestions for research and planning, one per paragraph. Each is answered by name in `research.md`.

FR-003 is the main risk. Keep the shipped Driver.js stylesheet byte-identical to its release: put it in a cascade layer rather than editing a copy of it.

For the defaults an installed app supplies (FR-009, FR-010), choose the least machinery that meets them, and look first for an existing Django mechanism before building any discovery of the package's own.
