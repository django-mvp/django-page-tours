# Planning notes — FS-005 Hints on a page

Suggestions for research and planning, one per paragraph. Each is answered by name in
`research.md`.

This feature comes from a prototype. Branch `prototype-hints-and-checklists`, its hand-over
`PROTOTYPE.md` at the branch root, record issue #45. This feature is the hand-over's section
"2. Hints on a page". Its screens are the demo page `/hints/` (`demo/templates/demo/hints.html`,
`demo/guides.py` `REPORT_HINTS` and `REPORT_TOUR`). The prototype's code is evidence of what the
screens do, never a base to build on.

The design rule every class follows, from the hand-over: every Python class mirrors a Driver.js
object; each option that takes a plain value is a field named exactly as Driver.js names it
(camelCase); top-level objects default each field to Driver.js's own default, and objects that
override a parent (a step, a hint, a beacon) default every field to `None`, which is left out of
the payload; nothing is checked beyond what the package itself depends on; options that take a
JavaScript function are not available, and the docs say so; text is passed to Driver.js as it is,
and default labels are lazy translated strings.

The shared pieces this feature builds, from the hand-over's table "The shared pieces". The
checklist specification (FS-006, issue #39) reuses each one, which is the second use Article III
asks for:

- **`DriverObject`.** "A dataclass that turns its fields into the Driver.js object: `None` left
  out, lazy strings rendered, nested objects and lists converted, fields routed into an inner
  object such as `popover`." Prototype: `page_tours/driver.py:37` `driver_value`, `:60`
  `DriverObject`. Becomes a base class. Built by hints, reused by the checklist. "`Tour` and
  `TourStep` move onto it in the hints feature, replacing `as_driver_steps` and the options
  comprehension in `__html__`."
- **`PopoverContent`.** "The popover fields a step and a hint share." Prototype:
  `page_tours/driver.py:94`, used at `tours.py:37`, `hints.py:50`. Becomes a base class. Built by
  hints, used by a step and a hint.
- **`Guide`.** "What a page renders: name, version, record of declared names,
  `PAGE_TOURS_OVERRIDES`, `{{ … }}` rendering, payload with `kind`." Prototype:
  `page_tours/driver.py:136` `Guide`, `:222` `resolve_override`, `:260`, `:270`; subclassed at
  `tours.py:87`, `hints.py:77`, `checklists.py:72`. Becomes a base class and the module functions
  it needs. Built by hints, reused by the checklist.
- **Rendering element id per kind.** "`page-tours-<kind>`." Prototype: `page_tours/driver.py:189`.
  Part of `Guide`. Built by hints, reused by the checklist. "Tours move from `page-tour-steps`."
- **The browser memory function.** "What the browser remembers: a list of ids under the guide's
  name, for its version." Prototype: `page-tours.js:26` `memory`. One function in the script.
  Built by hints, reused by the checklist and by the tour's seen record.
- **The popover part-classes function.** "Part classes on a popover, whatever shows it."
  Prototype: `page-tours.js:65` `popoverParts`. One function in the script. Built by hints, used by
  tours already and by checklist item tours.
- **The single play entry point.** "One entry point that plays every kind found on the page."
  Prototype: `page-tours.js:355` `play`. Part of the script. Built by hints, reused by the
  checklist.

Not this feature's: "Building a Driver.js tour from a tour's payload, with element lookup, part
classes, overlay naming, cleanup and seen record" (`page-tours.js:104` `buildTour`) is built by the
checklist, along with `Checklist`, `ChecklistItem` and `Offset`.

Duplication the hand-over asks the rebuild to remove, which falls to this feature because it
builds `Guide`: "`tours.py:151` `tour_overrides` and `:160` `declared_tours` only forward to the
`Guide` functions. The rebuild renames the callers (`apps.py`, `checks.py`) instead of keeping
aliases." "`page_tours/checks.py` W005 compares `repr(as_driver())` in the prototype as a quick
hack. The rebuild compares something meaningful per kind (a tour's steps, the hints, the items)."
"The error and messages still say "Tour" for every kind (`driver.py:222`)."

What the hand-over says the hints feature replaces: "In `tours.py`: `_declared`, `_forget`,
`resolve_override`, `tour_overrides`, `declared_tours`, `PACKAGE_FIELDS`, `STEP_LEVEL_FIELDS`,
`as_driver_steps` and the payload code in `__html__`, all moved onto the shared bases." "The tour
payload element `page-tour-steps` becomes `page-tours-tour`, and its `options` key becomes `config`
with the steps inside it." "The local storage key `page-tours:seen:<name>` and its value format."

Things noticed while specifying, for research to confirm: Driver.js 1.11.0's hints build names a
beacon whose hint has no title with its own English text, which the package cannot translate
without a title (G6); and the hints build watches for a tour starting and closes an open hint, but
whether it hides the beacons themselves, as the hand-over says, is to be confirmed in the browser.
