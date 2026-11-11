# django-page-tours — Domain Model

The vocabulary this repository uses. Specifications, issues, code and documentation use these
terms as defined here.

## Core concepts

### Tour

A short, guided walk through one page of a site, made of an ordered list of
[steps](#tour-step). A tour belongs to exactly one page. It is declared in Python by the
developer, next to the view that renders the page, with a [name](#tour-name), and shown in the
browser by Driver.js.

The view puts the tour in the page's template context under `tour`, like any other value, and the
page's template outputs it with `{{ tour }}`. A tour renders itself as the element the package's
script plays it from. Nothing finds the tour for the page. A page has one tour.

_Avoid:_ walkthrough, guide, onboarding (onboarding is the wider experience a tour may be part of).

### Tour step

One stop in a [tour](#tour): a title and a short text, usually attached to one element on the
page, which the tour highlights while the step is shown. A step attached to no element is shown
as a card in the middle of the page, which suits an opening welcome.

_Avoid:_ slide, popover (the popover is how a step is drawn, not the step itself).

### Part of a step

One named piece of a [step](#tour-step) as it is shown: the box, the title, the text, the
progress, a control (previous, next, done or close), or the [highlight](#highlight). Each has a
documented class name that a site styles.

### Highlight

What marks the step's element while the step shows.

### Seen

A tour has been seen in a browser once it has played there, whether the person finished it,
skipped it or closed it. A seen tour does not play again on its own. Seen is recorded in the
browser, never in the database, so the same person on a new browser has not seen it.

A tour is seen at a [version](#tour-version). A browser that saw another version of the tour has
not seen this one.

### Declaration

What a page renders: a [tour](#tour), [hints](#hints) or a [checklist](#checklist). Each has a name and a version, and all
share one namespace of names, so a name belongs to one declaration whichever kind it is. A browser
remembers what a visitor did under the name.

_Avoid:_ guide, config.

### Hints

The pointers a page shows over its elements, declared in Python as `Hints` with a
[name](#tour-name), a version and a list of [hints](#hint). The view puts them in the page's
template context under `hints`, and the page outputs them with `{{ hints }}`. Unlike a tour, they
do not take over the page: a visitor opens them in any order or not at all. A page has one set of
hints, and may have a tour as well.

_Avoid:_ tooltips, guide.

### Hint

One pointer in a set of [hints](#hints): the element it is about, a title and a description. It
shows a [beacon](#beacon) on its element, and opens a popover when the beacon is pressed. It is
remembered as dismissed by its identifier, or by its element when it has none.

_Avoid:_ tip, popover (the popover is how a hint is drawn).

### Beacon

The marker a [hint](#hint) shows on its element. A visitor presses it to open the hint. It is a
part of its own, `beacon`, that a site styles.

_Avoid:_ dot, pin.

### Dismissed hint

A [hint](#hint) whose button a visitor pressed. Its beacon is not shown again in that browser
until the hints' version is raised or the visitor uses the [restore control](#restore-control).
Recorded in the browser, never in the database.

_Avoid:_ closed, seen (seen is a tour that has played).

### Restore control

An element of the developer's own, marked `data-page-hints-restore`, that shows every
[dismissed hint](#dismissed-hint) again. Written `hidden`, it is shown only on a page with hints.

### Checklist

The panel a page shows in the corner of the window, listing what a visitor can do there. It is
declared in Python as `Checklist` with a [name](#tour-name), a version and a list of
[items](#checklist-item). The view or a context processor puts it in the template context under
`checklist`, and the page outputs it with `{{ checklist }}`. A page has one checklist, and may have
a tour and hints as well.

_Avoid:_ onboarding, to-do list, guide.

### Checklist item

One entry of a [checklist](#checklist): an id, a title and a description. Choosing it starts a
tour, opens an address, or does nothing, and it is [ticked](#ticked) by the app or by the visitor.

_Avoid:_ task, step (a step belongs to a tour).

### Ticked

A [checklist item](#checklist-item) is ticked once it is done. The app reports an item done when
the page is built, and a visitor ticks an item that allows it. The browser keeps the visitor's
ticks under the checklist's name and version, and never the app's report.

_Avoid:_ completed, checked (`completed` is the field the app reports ids in).

### Toggle control

An element of the developer's own, marked `data-page-checklist-toggle`, that opens a
[checklist](#checklist)'s panel and closes it again. Written `hidden`, it is shown only on a page
with a checklist.

### Tour version

A whole number the developer gives a tour, 1 unless they say otherwise. The developer raises it
when the tour has changed enough that people who saw it should see it again. It is never worked
out from the tour's steps, so a small edit keeps it.

### Tour name

The name the developer gives a [tour](#tour) where they declare it, `Tour(name="dashboard", ...)`.
Every tour has one. A browser remembers that a tour was [seen](#seen) by its name, and a project
changes an installed app's tour by naming it in [`PAGE_TOURS_OVERRIDES`](#tour-override).
Renaming the tour makes it a different tour; renaming or moving the view that shows it does not.
A reusable app names its tours `"<app_label>.<tour>"`.

_Avoid:_ tour id, slug, the view's path.

### Tour override

A project's replacement for the [tour](#tour) of an installed app, or its choice to turn that tour
off, set in `PAGE_TOURS_OVERRIDES` against the [tour name](#tour-name). A replacement plays under
the app tour's name and is seen at the app tour's [version](#tour-version) plus its own, less
one.

_Avoid:_ customisation, patch.

### Replay

Starting a tour again on request, whether or not it has been [seen](#seen).

### Driver.js

The MIT-licensed JavaScript library that draws a tour in the browser: it highlights each step's
element and shows the step beside it. The package ships a fixed release of it and never loads it
from a CDN.
