# Styling tours

The package ships Driver.js's own look, in the lowest cascade layer on the page, and nothing more.
This page shows how to give a tour the look of your site. Every piece of a shown step has a documented class name, so you style the tour
from your own stylesheet. You can also give a piece classes of your own, for example classes from
your CSS framework.

A piece of a shown step is called a part. A step has nine parts.

## The parts

| Part | Documented name | What it is |
|---|---|---|
| `box` | `page-tour-box` | The box that holds the step. |
| `title` | `page-tour-title` | The step's title. |
| `text` | `page-tour-text` | The step's text. |
| `progress` | `page-tour-progress` | The line that says where the visitor is in the tour. |
| `previous` | `page-tour-previous` | The control that goes back one step. |
| `next` | `page-tour-next` | The control that goes to the next step. It is on every step but the last. |
| `done` | `page-tour-done` | The control that ends the tour. It takes the place of `next` on the last step. |
| `close` | `page-tour-close` | The control that closes the tour. |
| `highlight` | `page-tour-highlight` | What marks the step's element while the step shows. |

A part carries its documented name on every step of every tour. The names are part of the public
surface of the package.

## Style the parts from your stylesheet

Write rules against the documented names in your own stylesheet:

```css
.page-tour-box {
  background: #1f2937;
  color: #f9fafb;
  border-radius: 0.75rem;
}

.page-tour-title {
  font-size: 1.125rem;
}

.page-tour-next,
.page-tour-done {
  background: #f59e0b;
  color: #1f2937;
}
```

Driver.js's rules sit in a cascade layer named `page-tours`. It is the lowest layer on the page
wherever your base template links `page_tours/page-tours.css`, because the package's script
moves that link to the start of the `<head>` before a tour plays. So a rule of yours that is outside any layer wins over Driver.js's whatever its order in the
page, and so do the layered classes of a framework. You never need `!important` to restyle a
part. The same layer means a rule you wrote for the page can reach a part of the tour, such as
`button { ... }` or a framework's layered reset. Style the documented names to settle any of it.

### Style the highlight with fill and fill-opacity

The highlight is an SVG shape drawn over the page, so it takes SVG properties and not the box
properties. Style it with `fill` and `fill-opacity`, or put an alpha in the `fill` colour:

```css
.page-tour-highlight {
  fill: #0f172a;
  fill-opacity: 0.8;
}
```

A `background` or `border` on the highlight is drawn across the whole page and washes over the
highlighted element, so use `fill`.

## Give parts classes with `PAGE_TOURS_CLASSES`

When your styles come from classes you already have, name them in the `PAGE_TOURS_CLASSES`
setting. It is a dict from a part to a string of class names:

```python
PAGE_TOURS_CLASSES = {
    "box": "rounded-lg shadow-xl",
    "next": "btn btn-primary",
    "done": "btn btn-primary",
    "previous": "btn btn-ghost",
}
```

A part carries these classes after its documented name, on every step of every tour in the
project. Things to know:

- **Values are strings.** Write several classes as one string separated by spaces.
- **An empty string means no classes.** `"close": ""` gives the close control only its
  documented name.
- **A part you leave out** carries only its documented name.
- **The setting is read each time a page renders,** so a change applies on the next request.

## Style tours from a design system

A design system that ships as a Django app can style the tour for every project that installs it.
It needs two things: rules against the documented names, and classes for the parts.

1. Put the rules against the documented names in the design system's own stylesheet. Its base
   template already loads that stylesheet, so the tour is styled wherever the base template is
   used.
2. Supply classes for the parts on the app's `AppConfig` as `page_tour_classes`. It is a dict from
   a part to a string of class names, the same shape as `PAGE_TOURS_CLASSES`:

   ```python
   from django.apps import AppConfig


   class DesignSystemConfig(AppConfig):
       name = "design_system"
       page_tour_classes = {
           "box": "card shadow-lg",
           "next": "btn btn-primary",
           "done": "btn btn-primary",
       }
   ```

A project that installs the app gets these classes with no settings of its own. Where they
conflict:

- **The project wins.** An entry in `PAGE_TOURS_CLASSES` replaces the app's classes for that part
  and for that part only. The app's classes for the other parts stay. An empty string clears a
  part, so `"close": ""` gives the close control only its documented name.
- **Between apps, the first in `INSTALLED_APPS` wins,** part by part. A part the first app leaves
  out takes the classes of the next app that names it.

`page_tour_classes` is part of the public surface of the package. Both warnings below name the app
an entry came from, so a design system's mistake is easy to find.

## Check the setting

Django's `check` command warns about an entry that cannot work, in the setting or in an app's
`page_tour_classes`:

- `page_tours.W003` says the entry names something that is not a part. The message lists the
  nine parts.
- `page_tours.W004` says a value is not a string of class names, or that the setting or the app's
  attribute is not a dict.

Both messages name the part, where there is one, and say where the entry came from: the setting,
or the app by its label. A wrong entry
is ignored when the page renders. It is never an error, so a mistake here cannot take a page
down.

## Read the parts from Python

`TourParts` holds the parts, their documented names and the classes each one carries. A project
that renders a step in its own way can read them from it:

```python
from page_tours.parts import TourParts

TourParts.parts          # the nine parts, in the order a step shows them
TourParts.name("box")    # "page-tour-box"
TourParts.classes()      # {"box": ["page-tour-box", "rounded-lg", ...], ...}
```

The full description of the class is in the [reference](../reference/api/index).
