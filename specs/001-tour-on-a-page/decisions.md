# Decisions — FS-001: A tour on a page

Readings taken while specifying, where issue #5 was silent. Each was chosen without a question to
the maintainer and is recorded here so it can be overruled.

## Readings the maintainer has already seen

1. **A step whose element is not on the page is skipped silently.** No error, no placeholder; the
   tour moves on. This is CONSTITUTION Article XIII applied to steps. A hidden element is treated
   the same way, because highlighting something the visitor cannot see helps nobody.
2. **A step attached to no element is shown on its own**, as CONTEXT.md describes, which suits an
   opening welcome.
3. **Step titles and texts are translatable.** They are the developer's own strings, so Article
   VIII applies to them now. The tour's own controls and a translation catalogue stay with R4.
4. **Tours work for signed-in and anonymous visitors alike.** Nothing about a visitor is needed to
   play a tour, and the package keeps nothing in the database.
5. **One tour belongs to one page.** No tours across several pages (README, "What it
   deliberately is not").
6. **The look is Driver.js's own** (Article XIV), so this feature carries no design work and no
   sketch.

## Self-resolved

7. **The tour plays every time the page opens.** Seen state, playing once per browser, the replay
   control and play-only-on-request are #6. This feature does not anticipate them beyond leaving
   room for them.
8. **Step text is plain text, escaped.** Driver.js accepts markup in a step's description, but
   passing developer strings through as markup opens an injection path the moment a step's text
   comes from data, and Article V requires escaping through the template layer. Markup in steps
   can be added later as a deliberate change if a need appears.
9. **Both class-based and function-based views can have a tour.** Django projects use both, and a
   package that served only one would leave half of every project out. How the tour attaches to
   each is a planning question.
10. **One-time setup in the base template is allowed.** "No JavaScript" (G1) is about each tour.
    Installing the app and placing the package's setup once in the base template is ordinary
    Django package setup and is not the developer writing JavaScript.
11. **A mistake in a declared tour is reported to the developer, not hidden from the visitor.** A
    tour with no steps, or a step without its title or text, is an error raised before any visitor
    sees the page. Skipping silently is reserved for what depends on the page at run time (a
    missing element), where the developer cannot know in advance.
12. **A step whose selector matches several elements attaches to the first.** This is Driver.js's
    own behaviour and the least surprising reading.
13. **A page with no tour loads nothing of the package.** A site that installs the package for one
    page should not pay for it on every other page, and Article XIII asks that a page without a
    tour be the same as without the package.
