# Tours from reusable apps

A reusable app can ship pages with tours of their own. A project that installs the app sees
those tours, and can replace any of them or turn it off, without editing the app.

## Ship a tour in a reusable app

If you write an app that other projects install, declare its tours on the app's views exactly as
a project does. See [Adding a tour to a page](tours.md).

1. Declare `tour` on a class-based view, or pass it in a function-based view's template context
   under `tour`.
2. Name each tour `"<app_label>.<tour>"`, starting with your app's label, such as
   `"library.book"`. Projects and other apps name their own tours, and the label keeps yours
   apart from theirs. The package cannot tell an app's tour from a project's, so nothing checks
   this rule, but `page_tours.W005` warns when two tours with different steps meet under one name.
3. Have the app's templates extend the project's base template. That is where a project
   places `{% page_tour %}` once, so the app's tours play with no setup of their own.
4. Treat a tour's name as part of what the app promises. Renaming a tour makes it a different
   tour: every visitor sees it again, and any override a project set for the old name stops
   matching. Renaming or moving the view that shows it changes nothing. Raising the tour's
   version shows it again, once, to everyone who saw it. Document the names of your app's
   tours, so a project can find them.

## Find the name of a tour

A project changes a tour by its name, the `name` the app gave it:

```python
class BookDetailView(TemplateView):
    template_name = "library/book_detail.html"
    tour = Tour(name="library.book", steps=[...])
```

This tour's name is `library.book`. The app's documentation should list its names. Otherwise
read the app's code, or open the page and read the name in the page source, where the tour's
payload carries it as `id`.

## Replace a tour from the project

Set `PAGE_TOURS_OVERRIDES` in the project's settings. Each key is the name of a tour, and each
value is the dotted path of a `Tour` to play in its place:

```python
PAGE_TOURS_OVERRIDES = {
    "library.book": "demo.tours.book_tour",
}
```

The replacement is an ordinary `Tour`, with a name of its own from the project. The page plays
it under the name of the tour it replaces, so what a browser remembers about the app's tour
still holds. To keep most of the app's tour, build it from the app's own steps. This one keeps
the first step and rewords the second:

```python
# demo/tours.py
from demo.library.views import BookDetailView
from page_tours import Tour, TourStep

book_tour = Tour(
    name="demo.book",
    steps=(
        *BookDetailView.tour.steps[:1],
        TourStep(
            title="Borrow it here",
            text="This library lends each book for a week. Press the button.",
            element="#library-borrow",
        ),
    )
)
```

The page keeps the app's template and view. Only the tour it plays changes.

## Turn a tour off

Give the name the value `None`:

```python
PAGE_TOURS_OVERRIDES = {
    "library.loans": None,
}
```

The page then has no tour, and a replay control placed in the base template does not show on it.

## Check that the setting is right

The setting is checked when the project starts, and read again each time a page renders.
`PageToursConfig.ready` calls `page_tours.tours.tour_overrides()`, which resolves every entry with
`page_tours.tours.resolve_override`. An entry whose value is neither a string nor `None`, whose
path cannot be imported, or whose path names something that is not a `Tour` raises
`ImproperlyConfigured` at start-up, naming the entry.

Django's `check` command warns with `page_tours.W002` when a key names no declared tour. The
usual cause is a misspelt name, or an app that renamed its tour. A tour is declared when the
module that holds it is imported, and the check loads the root URLconf first, so every tour in a
module the URLs import is known. A tour in a module that only a URLconf other than the root one
imports, for example one set per request, is not seen, so its key can draw the warning although
it works.

## Show a replacement to visitors who saw the app's tour

A replacement plays at the app tour's version plus its own version, less one. A visitor's
browser remembers the tour by its name and version, so this decides who sees the replacement:

- **Leave the replacement at version 1** and visitors who saw the app's tour do not see the
  replacement. It plays by itself only for a browser that has seen neither.
- **Raise the replacement's version** to show it again to everyone, once. At version 2 it plays at
  one more than the app's tour.
- **When the app releases a new version of its own tour,** every visitor sees the replacement
  once more, because the version it counts on from has moved.

## See it in the demo project

The demo project has a small app in `demo/library/` that stands for an installed app. Its
three pages are linked from the bar as Library. The book list plays the tour the app declared.
The book page plays the project's replacement, and the loans page has no tour. The project's
settings show the two entries, and the library app's own files are untouched.

## Why a tour's name is given by its developer

A name the app author writes down is the one thing that stays put while the app's code moves. It
is what a visitor's browser remembers a seen tour by, and what a project's override names, so
the same name serves both: renaming the tour makes a different tour for visitors and for
overrides alike, and renaming or moving the view changes neither. The decision is recorded in
ADR 0006.
