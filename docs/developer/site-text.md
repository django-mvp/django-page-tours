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

2. Open a page with a tour, hints or a checklist. Each one that does not word the text itself
   now shows yours.

Run `python manage.py check` to have a mistake in the setting reported.

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

A text that you set on a tour, on hints or on a checklist wins over the setting. A text that you set on a step or a hint wins over both:

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

The setting is read every time a tour, hints or checklist renders, so it can be changed in a test
with `override_settings`. Driver.js writes these texts into the page as HTML, so never build one
from a visitor's input.

## Why the setting changes only text left alone

A declaration that sets nothing takes the setting, and one that sets a text keeps it, so a tour
written for one place does not change when the site's wording does. A tour that sets a text to
the package's own text, say `nextBtnText="Next"`, keeps "Next".
