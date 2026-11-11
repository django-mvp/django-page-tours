# Planning notes — FS-006 A checklist

## The prototype

This feature is specified from the prototype on branch `prototype-hints-and-checklists`, recorded
on issue #45. Its hand-over is `PROTOTYPE.md` at the root of that branch. This feature's part is
the section "3. A checklist". Its screens are the checklist on every demo page, through the context
processor `demo.guides.onboarding`, and the book page `/library/book/`, which ticks an item from
the app. The prototype's code is evidence for the build, never its base.

The design rule every class follows, from the hand-over:

- Each option that takes a plain value is a field, named exactly as Driver.js names it
  (camelCase).
- Top-level objects default each field to Driver.js's own default. Objects that override a parent
  default every field to `None`, and a `None` is left out of the payload, so the parent's value
  applies.
- Nothing is checked for the developer beyond what the package itself depends on. A value that
  cannot be serialised fails in `json_script`, and that is enough.
- Options that take a JavaScript function are not available, and the docs say so.
- Text is passed to Driver.js as it is. Default labels are lazy translated strings.

## The shared pieces

The rows of the hand-over's "The shared pieces" that this feature builds or reuses, in its words.
Research answers each by name.

### Reused: a base class, `DriverObject`

A dataclass that turns its fields into the Driver.js object: `None` left out, lazy strings
rendered, nested objects and lists converted, fields routed into an inner object such as
`popover`. Prototype: `page_tours/driver.py:37` `driver_value`, `:60` `DriverObject`. Built by
hints (FS-005). `Checklist`, `ChecklistItem` and `Offset` are declared on it.

### Reused: the base class for what a page renders, and the module functions it needs

What a page renders: name, version, record of declared names, `PAGE_TOURS_OVERRIDES`, `{{ … }}`
rendering, payload with `kind`. Prototype: `page_tours/driver.py:136` (named `Guide` in the prototype), `:222`
`resolve_override`, `:260`, `:270`; subclassed at `checklists.py:72`. Built by hints (FS-005).
`Checklist` is declared on it, under whatever name FS-005 gives it. The prototype's name is
not kept, because `CONTEXT.md` avoids the word.

### Reused: rendering element id per kind, part of the base class for what a page renders

`page-tours-<kind>`. Prototype: `page_tours/driver.py:189`. Built by hints (FS-005). The checklist
renders as `page-tours-checklist`.

### Reused: one function in the script for what the browser remembers

A list of ids under the guide's name, for its version. Prototype: `page-tours.js:26` `memory`.
Built by hints (FS-005). The checklist keeps its ticks with it, and the tour's seen record, which
an item's tour writes, is kept with it too.

### Reused: one function in the script for part classes on a popover

Part classes on a popover, whatever shows it. Prototype: `page-tours.js:65` `popoverParts`. Built
by hints (FS-005). Reused by checklist item tours.

### Built here: one function in the script that builds a Driver.js tour

Building a Driver.js tour from a tour's payload, with element lookup, part classes, overlay
naming, cleanup and seen record. Prototype: `page-tours.js:104` `buildTour`; used at `:199` and
`:328`. Built by the checklist. Reused by the page's own tour, which moves onto it in this
feature.

### Reused: one entry point that plays every kind found on the page

Part of the script. Prototype: `page-tours.js:355` `play`. Built by hints (FS-005). The checklist
adds its player to it.

## Also from the hand-over

- The prototype's checklist item tour is not looked up in `PAGE_TOURS_OVERRIDES`. The hand-over
  lists that as faked, and the checklist does it properly (decision D5).
- The prototype's system check for one name declared twice compares `repr(as_driver())`. The
  rebuild compares something meaningful per kind; for a checklist, its items.
- Driver.js 1.11.0 reports a finished tour as ended by the page while `onDestroyStarted` is set,
  so the tour's cleanup must run in `onDestroyed` (issue #46). An item's tick depends on it.
