# django-page-tours — Domain Model

The vocabulary this repository uses. Specifications, issues, code and documentation use these
terms as defined here.

## Core concepts

### Tour

A short, guided walk through one page of a site, made of an ordered list of
[steps](#tour-step). A tour belongs to exactly one page. It is declared in Python by the
developer, next to the view that renders the page, and shown in the browser by Driver.js.

_Avoid:_ walkthrough, guide, onboarding (onboarding is the wider experience a tour may be part of).

### Tour step

One stop in a [tour](#tour): a title and a short text, usually attached to one element on the
page, which the tour highlights while the step is shown. A step attached to no element is shown
as a card in the middle of the page, which suits an opening welcome.

_Avoid:_ slide, popover (the popover is how a step is drawn, not the step itself).

### Seen

A tour has been seen in a browser once it has played there, whether the person finished it,
skipped it or closed it. A seen tour does not play again on its own. Seen is recorded in the
browser, never in the database, so the same person on a new browser has not seen it.

A tour is seen at a [version](#tour-version). A browser that saw another version of the tour has
not seen this one.

### Tour version

A whole number the developer gives a tour, 1 unless they say otherwise. The developer raises it
when the tour has changed enough that people who saw it should see it again. It is never worked
out from the tour's steps, so a small edit keeps it.

### Tour name

The dotted path of the view that declares a [tour](#tour): for a class-based view, the class whose
own body sets `tour`, and for a function-based view, the function `with_tour` decorates. A browser
remembers that a tour was [seen](#seen) by its name, and a project changes an installed app's tour
by naming it in [`PAGE_TOURS_OVERRIDES`](#tour-override). Renaming or moving the view gives the
tour a new name.

_Avoid:_ tour id, slug.

### Tour override

A project's replacement for the [tour](#tour) of an installed app, or its choice to turn that tour
off, set in `PAGE_TOURS_OVERRIDES` against the [tour name](#tour-name). A replacement is seen at
the app tour's [version](#tour-version) plus its own, less one.

_Avoid:_ customisation, patch.

### Replay

Starting a tour again on request, whether or not it has been [seen](#seen).

### Driver.js

The MIT-licensed JavaScript library that draws a tour in the browser: it highlights each step's
element and shows the step beside it. The package ships a fixed release of it and never loads it
from a CDN.
