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

### Replay

Starting a tour again on request, whether or not it has been [seen](#seen).

### Driver.js

The MIT-licensed JavaScript library that draws a tour in the browser: it highlights each step's
element and shows the step beside it. The package ships a fixed release of it and never loads it
from a CDN.
