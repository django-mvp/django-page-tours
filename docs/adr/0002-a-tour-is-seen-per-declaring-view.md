# ADR 0002 — A tour is seen per the view that declares it

**Status:** superseded by ADR 0006

## Decision

The browser remembers that a tour has been seen under the dotted path of the view that declares
it, in `localStorage`, under the key `page-tours:seen:<dotted path>`.

- A class-based view: the first class along the view's method resolution order whose own body
  sets `tour`. A subclass that inherits its parent's tour shares the parent's seen state, and a
  subclass that sets its own tour has its own. When no class body holds the tour (it was set on
  the instance, or through `as_view(tour=...)`), the view's own class is used.
- A function-based view: the function `@with_tour` decorates, which the decorator records on
  `request.page_tour_view`.

`tour_id(context)` in `page_tours/tours.py` holds this rule, and `{% page_tour %}` sends its result
to the browser with the tour.

## Why

Seen has to belong to the tour, not the address, so a tour on every record's detail page is seen
once. It has to stay the same when a tour's steps are edited, because showing a changed tour
again is a separate, later decision (tour versions). And playing once must need no setting from
the developer.

- A hash of the steps changes whenever a step is edited, so every edited tour would play again.
- A name the developer gives each tour is a setting every tour would need.
- The declaring view is already how a tour is found (ADR 0001), is the same on every address the
  view serves, and does not change when the steps do.

## Consequences

- Renaming or moving the view makes its tour unseen in every browser, so it plays again once.
- Per-URL tours on one class (`as_view(tour=...)`) share one seen state.
- The view's dotted path is visible in the page's source.
- Changing this rule later makes every tour on every site play again once, which is why it is
  recorded here.

## Revisit if

- Tours gain versions, so a changed tour can be shown again on purpose.
- A site needs two tours declared on one class to be seen separately.
