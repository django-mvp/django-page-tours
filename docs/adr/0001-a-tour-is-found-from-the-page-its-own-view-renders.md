# ADR 0001 — A tour is found from the page its own view renders

**Status:** superseded by ADR 0007. Amended by ADR 0006 for function-based views.

## Decision

`{% page_tour %}` finds a page's tour from what the view's own rendering puts in the template
context, never from the URL that was requested.

- A class-based view declares `tour` as an attribute. The tag reads it from `context["view"]`,
  which Django's generic views put in the context (`ContextMixin.get_context_data`).
- A function-based view passes the tour in its template context under `tour`. Until ADR 0006 it
  was decorated with `@with_tour(...)`, which set `request.page_tour` before calling the view and
  removed it again if the view raised.

`Tour.for_page(context)` holds this rule, and the tag calls it.

## Why

A tour belongs to the view that renders the page. The obvious lookup is the view the URL
resolved to, `request.resolver_match.func`, but that view is still recorded when it raises
`Http404` or `PermissionDenied`. Django's 404 and 403 handlers then render their page with the
same request. A tour found that way would play over the error page, and to a visitor who was
refused permission it would describe a page they may not see. A class-based view puts itself in
the context only when it renders its own page, and a function-based view's context exists only
when it renders its own page too. An error page is rendered with a context of its own. So both
lookups see the page's own rendering and nothing else.

## Revisit if

- A class-based view that does not put `view` in its context needs a tour. That means one not
  built on Django's generic views, or one that overrides `get_context_data` without calling
  `super()`.
- Tours are to be chosen per request rather than declared per view.
