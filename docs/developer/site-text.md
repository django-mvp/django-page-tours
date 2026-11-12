# Word every tour on the site

A tour says "Next", "Previous" and "Done", a set of hints says "Got it" and a checklist says
"Get started". This page shows how to change that text once for the whole site, with the
`PAGE_TOURS_TEXT` setting, instead of on every tour.

## Change the text of the whole site

1. Add `PAGE_TOURS_TEXT` to your settings. Key it by the kind of declaration, `"tour"`, `"hint"`
   or `"checklist"`, and then by the name of the text:

   ```python
   PAGE_TOURS_TEXT = {
       "tour": {"nextBtnText": "Continue", "doneBtnText": "Finish"},
       "hint": {"buttonText": "Understood"},
       "checklist": {"title": "Your first steps"},
   }
   ```

2. Restart the server. The setting is read once, when the package is imported, like most Django
   settings.

3. Open a page with a tour, hints or a checklist. Each one that does not word the text itself
   now shows yours.

A kind or name the package does not have is ignored, so check the spelling against the table
below.

## The texts

The names are the fields of the declarations, spelled as Driver.js spells them.

| Kind | Text | What it is |
|---|---|---|
| `"tour"` | `progressText` | The progress text, with `{{current}}` and `{{total}}`. |
| `"tour"` | `nextBtnText` | The text of the next button. |
| `"tour"` | `prevBtnText` | The text of the previous button. |
| `"tour"` | `doneBtnText` | The text of the button on the last step. |
| `"tour"` | `closeBtnLabel` | The accessible name of the close button. |
| `"hint"` | `buttonText` | The text of the button of every popover of a set of hints. |
| `"checklist"` | `title` | The heading of the checklist. |
| `"checklist"` | `progressText` | The progress in the panel, with `{{done}}` and `{{total}}`. |
| `"checklist"` | `launcherProgressText` | The progress on the launcher. |

A tour in a checklist item takes the `"tour"` texts, as a tour on a page does. A tour, hints or
checklist that `PAGE_TOURS_OVERRIDES` replaces takes them too.

## Give one tour its own text

A text that you set on a tour, on hints or on a checklist, or as the default of a subclass of
one, wins over the setting. A text that you set on a step or a hint wins over both:

```python
Tour(
    name="dashboard",
    steps=[
        TourStep(title="Welcome", nextBtnText="Show me"),
        TourStep(title="Reports"),
    ],
    doneBtnText="Got it",
)
```

Here the first step's button says "Show me", the last step's button says "Got it", and every
other text comes from `PAGE_TOURS_TEXT`, or else from the package.

## Translate the text

A value is a string, or a lazy translation that is converted when the page renders, in the
visitor's language:

```python
from django.utils.translation import gettext_lazy as _

PAGE_TOURS_TEXT = {"tour": {"nextBtnText": _("Continue")}}
```

Driver.js writes these texts into the page as HTML, so never build one
from a visitor's input.

## How the setting works

The setting replaces the package's own default of each text it names. A declaration that sets
nothing takes that default, and one that sets a text keeps it, so a tour written for one place
does not change when the site's wording does.

Because the setting is read at import, `override_settings` in a test does not change it. Set it
in the settings module your tests run with.
