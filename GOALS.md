# Goals

These are the standing directions `django-page-tours` works toward. Each one is a capability or
quality to steer by, not a task that gets ticked off. Whether any goal has been served well enough
is decided in the roadmap, the feature specs, and review, never by the goal itself.

This file carries no version numbers or release plan; that lives in the roadmap. For what the
package is, what it stays out of, and the principles that settle a close call, read the
*Scope & philosophy* section of the [README](README.md).

Importance is a tag on each goal, not a ranking:

- **Essential** — not worth adopting without it.
- **Expected** — a complete, dependable version is expected to have it.
- **Aspirational** — a genuine want whose absence never makes the package incomplete.

| ID | Goal | Importance | Status | Notes |
|----|------|------------|--------|-------|
| G1 | A developer declares a tour for a page in Python, beside the view that renders it, without writing JavaScript | Essential | | |
| G2 | A tour plays once for each visitor and then stays out of their way, until they ask to see it again | Essential | | |
| G3 | Tours work on installation, with nothing fetched from another origin and no front-end build step | Essential | | |
| G4 | A tour never makes its page less usable, whether its elements are missing, its script fails or JavaScript is off | Essential | | |
| G5 | Tours can be followed with a keyboard and a screen reader | Expected | | |
| G6 | Tours speak the visitor's language | Expected | | |
| G7 | A site gives tours its own look, and a design system can style them for every site built on it | Expected | | |
| G8 | A reusable app ships tours for its own pages, which a project can change or turn off without editing the app | Expected | | |
| G9 | When a tour changes enough to matter, people who saw the old one see it again | Expected | | |

_Written 2026-11-06. Revise as the goals change._
