# Tours from reusable apps

A reusable app can ship pages with tours of their own. A project that installs the app sees
those tours, and can replace any of them or turn it off, without editing the app.

## Ship a tour in a reusable app

If you write an app that other projects install, declare its tours on the app's views exactly as
a project does. See [Adding a tour to a page](tours.md).

1. Declare `tour` on a class-based view, or decorate a function-based view with `with_tour`.
2. Render the app's pages through a template that loads the tour tag. The tag belongs in the
   project's base template, so the app's templates extend the project's base template and the
   project places `{% page_tour %}` in it once.
3. Treat a change to a tour's name as a change the installing projects see. A tour's name is the
   dotted path of the view that declares it, so renaming or moving that view gives the tour a
   new name: every visitor sees it again, and any override a project set for the old name stops
   matching. Raising the tour's version also shows it again, once, to everyone who saw it.

## Find the name of a tour

A project changes a tour by its name. The name is the dotted path of the view that declares the
tour:

- **For a class-based view,** it is the class whose own body sets `tour`. A subclass that
  inherits the tour shares its parent's name. `page_tours.tours.declaring_view_name` returns
  this name for a view class.
- **For a function-based view,** it is the function that `with_tour` decorates.

For a book page declared as `class BookDetailView(TemplateView)` in the `demo.library.views`
module, the name is `demo.library.views.BookDetailView`.

## Replace a tour from the project

Set `PAGE_TOURS_OVERRIDES` in the project's settings. Each key is the name of a tour, and each
value is the dotted path of a `Tour` to play in its place:

```python
PAGE_TOURS_OVERRIDES = {
    "demo.library.views.BookDetailView": "demo.tours.book_tour",
}
```

The replacement is an ordinary `Tour`. To keep most of the app's tour, build it from the app's
own steps. This one keeps the first step and rewords the second:

```python
# demo/tours.py
from demo.library.views import BookDetailView
from page_tours import Tour, TourStep

book_tour = Tour(
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
    "demo.library.views.LoansView": None,
}
```

The page then has no tour, and a replay control placed in the base template does not show on it.

## Check that the setting is right

The setting is read when the project starts. `PageToursConfig.ready` calls
`page_tours.tours.tour_overrides()`, which resolves every entry with
`page_tours.tours.resolve_override`. An entry whose value is neither a string nor `None`, whose
path cannot be imported, or whose path names something that is not a `Tour` raises
`ImproperlyConfigured` at start-up, naming the entry.

Django's `check` command warns with `page_tours.W002` when a key names no tour that a view in
the project's URLs declares. The usual cause is a misspelt name, or an app that renamed the view.
The check reads the root URLconf only. A view reached through a URLconf that is not the root one,
for example one set per request, is not seen, so its key can draw the warning although it works.

## Show a replacement to visitors who saw the app's tour

A replacement plays at the app tour's version plus its own version, less one. A visitor's
browser remembers the tour by its name and version, so this decides who sees the replacement:

- **Leave the replacement at version 1** and visitors who saw the app's tour do not see the
  replacement. It plays by itself only for a browser that has seen neither.
- **Raise the replacement's version** to show it again to everyone, once. At version 2 it plays at
  one more than the app's tour.
- **When the app releases a new version of its own tour,** every visitor sees the replacement
  once more, because the version it counts on from has moved.

## Why a tour's name is a view's path

The view that declares a tour is the one thing both the app author and the project can name
without the package keeping a list. It is also what remembers that a tour was seen in a
visitor's browser, so the same name serves both purposes: renaming a view makes a different tour
for visitors and for overrides alike.

## See it in the demo project

The demo project has a small app in `demo/library/` that stands for an installed app. Its
three pages are linked from the bar as Library. The book list plays the tour the app declared.
The book page plays the project's replacement, and the loans page has no tour. The project's
settings show the two entries, and the library app's own files are untouched.
