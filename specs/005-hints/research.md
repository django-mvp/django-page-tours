# Research — FS-005 Hints on a page

Planned at `4aecfd2`: `main` at `9266abc` with pull requests #43 (a tour and its steps declare
Driver.js's options as fields) and #54 (Driver.js 1.11.0 and `advanceOn`) merged in, because this
feature builds on both. The agreed design is the prototype at `0424c5a`
(`prototype-hints-and-checklists`, hand-over `PROTOTYPE.md`, record issue #45).

## Assumptions checked

- **Driver.js 1.11.0's hints build takes the options the specification mirrors.** Read in the
  vendored `page_tours/static/page_tours/vendor/driver.js-1.11.0/hints.iife.js`: the hints
  configuration reads `hints`, `beacon`, `buttonText`, `popoverClass`, `popoverOffset` (default
  10), `overlay`, `overlayColor` (default `#000`) and `overlayOpacity` (default 0.7). A hint reads
  `element`, `id`, `beacon` and `popover`, and the popover reads `title`, `description`, `side`
  (default `bottom`), `align` (default `start`), `popoverClass`, `showButton` (default true) and
  `buttonText`. A beacon reads `side`, `align`, `animate`, `className`, `offsetX` and `offsetY`.
  The function options are `onDismiss`, `onButtonClick` and the popover's `onPopoverRender`.
  Confirmed.
- **A hint's beacon merges over the hints' beacon field by field.** The build reads a hint's
  beacon as `{...config.beacon, ...hint.beacon}`, so a beacon field left out of a hint's beacon
  falls back to the hints' beacon. A `None` left out of the payload is therefore enough for
  FR-003, with no merging in the package. Confirmed.
- **A hint's button and class fall back the same way.** `hint.popover.buttonText ??
  config.buttonText ?? "Got it"` and `hint.popover.popoverClass || config.popoverClass`.
  Confirmed.
- **Beacons are keyboard reachable.** Each beacon is a `<button type="button">` with
  `aria-haspopup="dialog"` and `aria-expanded`, and the popover is a dialog labelled by its title.
  A beacon whose hint has no title is named with Driver.js's own English "Show hint". Confirmed.
- **No beacon pulses under reduced motion.** `hints.css` turns the pulse animation off under
  `prefers-reduced-motion: reduce`. Confirmed.
- **The hints build is its own global.** `hints.iife.js` defines `window.driverHints.hints` and
  does not need `driver.js.iife.js`. A page with hints loads it with one more `<script>`.
  Confirmed.
- **The prototype's hints page renders.** `http://devserver:8037/hints/` returns 200 with the
  hints payload element, the restore control and the hints build. Confirmed.

## Planning notes, answered

**The prototype and its hand-over.** Adopted as the agreed design. Its screen is the demo page
`/hints/`, rebuilt from `demo/templates/demo/hints.html`, `REPORT_HINTS` and `REPORT_TOUR`. Its
code is read as evidence and rebuilt test-first. Two points of its code are not followed, both
below: the base's name, and the beacon's class when a hint sets no class of its own.

**The design rule every class follows.** Adopted unchanged (`decisions.md` D3). Every class is a
frozen dataclass, keyword-only, with Driver.js's names. `Hints` defaults each option to Driver.js's
default. `Hint` and `Beacon` default every field to `None`, and a `None` is left out. Nothing is
checked beyond the package's own `name` and `version`. No function option is a field.

**`DriverObject`.** Adopted, in a new module `page_tours/driver.py`. A frozen dataclass with one
method, `as_driver()`, and two class attributes: `package_fields`, the fields Driver.js never
receives, and `nested`, the inner object a field goes into (`popover`). One module function,
`driver_value()`, converts a value: another `DriverObject` to its object, a tuple or list to a
list, a lazy string to its text, anything else as it is. `TourStep`, `Tour`, `Hint`, `Beacon` and
`Hints` use it now, and FS-006's `Checklist`, `ChecklistItem` and `Offset` use it next.

**`PopoverContent`.** Adopted: `title`, `description`, `side`, `align` and `popoverClass`, each
defaulting to `None`, and a class attribute naming them as the popover's fields. `TourStep` and
`Hint` are its two uses.

**`Guide`, the base of what a page renders.** Adopted, named `Declaration` (D11). `CONTEXT.md`
already calls making a `Tour(...)` declaring it ("A tour is declared when it is made"), the
specification calls a tour or a set of hints "a declaration" throughout (FR-009, D5, D7), and the
word avoids "guide", which `CONTEXT.md` lists to avoid. `CONTEXT.md` gains the term. It holds
`name` and `version`, refuses a bad one with `ImproperlyConfigured`, records itself in the
registry of declared names, renders with `{{ … }}` (applying `PAGE_TOURS_OVERRIDES`), and builds
the payload with `kind`. Its module functions are `resolve_override`, `declaration_overrides`
and `declarations`.

**Rendering element id per kind.** Adopted: `page-tours-<kind>`, so `page-tours-tour` and
`page-tours-hints`. The tour's `page-tour-steps` goes, and its `options` become `config`, with the
steps inside it, as Driver.js takes them.

**The browser memory function.** Adopted as `memory(kind, payload)` in `page-tours.js`: a list of
ids kept under `page-tours:<kind>:<name>` as `{"version": …, "ids": […]}`, read as empty when the
stored version is another one or the storage cannot be read. The tour's seen record moves onto it
under `page-tours:seen:<name>`. The old value there is a bare version number, which reads as
nothing stored, so a tour seen before plays once more (D7, FR-021).

**The popover part-classes function.** Adopted as `popoverParts(parts)`, returning the
`onPopoverRender` both a tour and a hint pass to Driver.js.

**The single play entry point.** Adopted as `play()`, which looks for each kind's element, hints
first so a tour step can point at a beacon, and plays each one inside its own `try`, so a failure
of one kind leaves the others and the page as they were (FR-018).

**Building a Driver.js tour from a payload.** Not this feature's (the hand-over gives it to the
checklist). The tour code in `page-tours.js` keeps its present shape and its workarounds for
1.11.0 (focus put back, closing while a step opens, the error handler), and only reads its
payload from the new element and `config`.

**Duplication to remove.** Adopted. `tour_overrides` and `declared_tours` go, and their callers in
`apps.py` and `checks.py` call `declaration_overrides` and `declarations`. W005 compares what makes
two declarations the same one: their class and their content field (a tour's `steps`, the hints'
`hints`), never a `repr`. Messages name the class that is wrong (`Tour`, `Hints`), never "Tour"
for every kind.

**What the hints feature replaces in `tours.py`.** Adopted: `_declared`, `_forget`,
`resolve_override`, `tour_overrides`, `declared_tours`, `PACKAGE_FIELDS`, `STEP_LEVEL_FIELDS`,
`as_driver_steps` and the payload code in `__html__` move onto the bases or go.

**A beacon without a title is named in English by Driver.js (G6).** Not adopted as package code.
The build names a beacon with its hint's title and falls back to its own "Show hint", which is not
an option. Giving every hint a title is what makes its beacon named in the page's language, so the
documentation says to give every hint a title. Adding a fallback title would put text on the
popover the developer did not write.

**Whether the hints build hides the beacons during a tour (D12).** Settled from the code. The
script only closes an open hint when a tour starts, but `hints.css` holds
`.driver-active .driver-hint { display: none }`, and Driver.js puts `driver-active` on the body
while a tour plays. So Driver.js meets FR-015 once its hints stylesheet is on the page. The
package's stylesheet imports it into the same lowest layer as `driver.css` (ADR 0005), and the
package adds no code for it. A browser test asserts the behaviour.

## Decisions taken at research

**Every declaration class is keyword-only.** `Declaration` has a default (`version`) ahead of the
subclass fields without one (`steps`, `hints`), which a dataclass allows only keyword-only. Every
tour in this repository's docs, demo and tests is declared with keywords already, so FR-021 holds
for them. A `TourStep(...)` written with positional arguments stops working, which the changelog
says (`decisions.md` D13).

**An override's replacement must be of the declaration's own class.** At start-up a replacement
must be a `Declaration`, since the original may not be imported yet. When the original renders,
the replacement must be of its class, or rendering raises `ImproperlyConfigured` naming the entry
(FR-010). The check is of the package's own setting, not of a Driver.js option (D5).

**A beacon carries its part's classes ahead of its own class, and keeps the hints' class.** The
prototype writes the beacon part's classes and the hint's own `className` into the hint's beacon,
which replaces the hints' `beacon.className` for a hint that sets none. The rebuild writes the
part's classes, then the hint's `className`, else the hints' (FR-019, US3 scenario 2).

**A hint's button carries the `next` part.** The build draws the button as Driver.js's next
button. The prototype names it `next`, as a tour's next button, and the rebuild keeps that.

## What already exists

- `DriverObject.as_driver()`: **new code**. This repo has `Tour.as_driver_steps` and the options
  comprehension in `Tour.__html__`, which it replaces. `dataclasses.asdict` (standard library)
  does not leave out `None`, route a field into `popover` or render a lazy string, and turns every
  nested dataclass into a dict before the package can choose.
- `driver_value()`: **new code**, the four conversions above.
- `PopoverContent`: **new code**, five fields moved from `TourStep`.
- `Declaration` and its registry, `resolve_override`, `declaration_overrides`, `declarations`:
  **this repo**, moved from `page_tours/tours.py`, where `_declared`, `_forget`,
  `resolve_override`, `tour_overrides` and `declared_tours` do this for tours.
- Rendering `{{ hints }}`: **Django**, `django.utils.html.json_script`, as for a tour.
- `Hints`, `Hint`, `Beacon`: **new code**, dataclass fields only.
- The default button text: **Django**, `pgettext_lazy`.
- W005 across kinds, W002 and W003/W004 for the beacon: **this repo**, `page_tours/checks.py`,
  extended. The beacon part is one entry in `TourParts.parts`.
- Beacons, popovers, dismissal for the page view, keyboard operation, reduced motion, hiding the
  beacons during a tour: **an installed package**, Driver.js 1.11.0's hints build and `hints.css`,
  already vendored by #54.
- `memory()`: **new code**, replacing the tour's `isSeen`/`markSeen` pair with one function both
  kinds use. `localStorage` is the browser's.
- `popoverParts()`: **this repo**, the tour's `nameParts`, made to take its parts.
- Restore control: **this repo**, the replay control's pattern (`hidden`, shown by the script).
