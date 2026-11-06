# Research — FS-002 Seen tours and replay

## Assumptions checked

- **A tour on a page (issue #5) is not built yet.** On `main` at the time of writing, the package
  holds only its app configuration: there is no tour declaration, no template output and no
  shipped Driver.js to load and run. This feature extends that one, so the build starts once it
  has merged. Nothing could be run here, and the build re-checks every surface it extends against
  the merged code.
- **No dependency on Driver.js reporting how a tour ended.** Seen is recorded when the tour starts
  (spec FR-002), so the specification assumes nothing of Driver.js beyond starting a tour on
  request, which issue #5 already needs.
