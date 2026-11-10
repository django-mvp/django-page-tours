# ADR 0006 — A tour is named by its developer

**Status:** accepted. Supersedes ADR 0002 and ADR 0004.

## Decision

A tour carries a name, given where it is declared: `Tour(name="dashboard", steps=[...])`. The
name is required and is the tour's identity everywhere.

- The browser remembers a seen tour under `page-tours:seen:<name>`, holding the version that
  played (ADR 0003).
- A project replaces or turns off an installed app's tour with `PAGE_TOURS_OVERRIDES`, keyed by
  tour name. Each value is the dotted path of a replacement `Tour`, or `None` to turn the tour off,
  and every entry is resolved when the project starts. A replacement has a name of its own, and
  plays under the name of the tour it replaces, at that tour's version plus its own, less one.
  These rules are carried over from ADR 0004 unchanged except for the key.
- A class-based view keeps its `tour` attribute. A function-based view passes its tour in the
  template context under `tour`. `Tour.for_page` takes the view's attribute first, then the
  context's `tour`, and only a `Tour` counts.
- Every `Tour` is recorded under its name when it is made, by weak reference.
  `page_tours.W002` warns about an override key that names no recorded tour, after loading the
  root URLconf so the routed views' tours are recorded. `page_tours.W005` warns when tours with
  different steps are recorded under one name.
- A reusable app names its tours `"<app_label>.<tour>"`. This is documented, not checked.

`with_tour`, `tour_id`, `declaring_view_name`, the method-resolution-order rule and the
`page_tours.W001` check for the request context processor are removed. Nothing else needs the
request.

## Why

ADR 0002 avoided a developer-given name because every tour would need one. Getting a stable name
from a view instead took more than a setting would have:

- A function-based view that passed its tour in its context gave the tag the tour but no name, so
  `with_tour` existed to put the tour and the function's path on the request. That made the
  request context processor a requirement, with a check of its own.
- A class-based view was named by walking its method resolution order for the class whose own
  body sets `tour`, so a subclass shared its parent's seen state.
- Renaming or moving a view replayed its tour for every visitor and broke any override set for
  the old path. A reusable app could not reorganise its code without breaking the projects that
  changed its tours, which ADR 0004 listed as the thing to revisit.
- The view's dotted path was in every page's source.

ADR 0004's reasons for the setting's shape still hold: it has Django's `MIGRATION_MODULES` shape,
its values are paths because settings load too early to import an app's views, and counting the
version on from the app tour's keeps a replacement quiet for visitors who saw the app's tour while
leaving the project a way to show it again.

A name the developer writes down stays put while the code moves, needs no machinery to find, and
is one keyword argument per tour. It also answers ADR 0002's open case: two tours given to one
view class through `as_view(tour=...)` now have their own seen states when they have their own
names.

- **Steps, not equality, decide a clash.** One tour routed at two versions, or declared with and
  without autoplay, is one tour that a developer is trying out, and sharing a seen state is what
  they want. Tours with different steps under one name are two tours, and the warning catches
  the accident.
- **The registry holds weak references,** so a tour nothing refers to any more, such as one made
  in a test, does not stay declared. The tour a page plays for a replacement is copied rather
  than constructed, so it is never recorded as a second tour.
- **The app-label rule is not checked.** The package cannot tell a reusable app's tour from a
  project's own, so a check would warn about every project tour too.

## Consequences

- Every tour plays once more after the upgrade, because what browsers remembered is stored under
  the old view-based names. The changelog says so.
- Every `PAGE_TOURS_OVERRIDES` key has to be rewritten as a tour name.
- A tour's name is part of what a reusable app promises the projects that install it. Renaming a
  tour, rather than its view, is now the change those projects see.
- A tour's name is visible in the page's source.
- A tour declared in a module that nothing imports by the time the checks run is not known to
  `page_tours.W002`.

## Revisit if

- A site needs one declared tour to be seen separately per page that shows it.
- Tours come to be built per request, so recording them at import no longer describes them.
