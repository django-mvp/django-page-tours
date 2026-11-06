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

## Planning

14. **Browser installation in CI is set up outside this branch.** The browser tests need the
    shared tests workflow called with `install-playwright: true`. That change lands on main as
    its own pull request, and this branch is rebased onto it before it is marked ready for
    review, so no workflow file changes here.
15. **A tour plays only on the page its own view renders, never on an error page shown in its
    place.** A view with a tour that raises `Http404` or `PermissionDenied` is followed by a 404
    or 403 page rendered with the same request. Looking the tour up from the URL's view would
    play it there, including to a visitor refused the page. The tag reads the class-based view
    from the context, and `with_tour` marks the request only while its view runs without error.
16. **Driver.js's step count stays off.** It counts skipped steps, so a tour with a missing
    element would count steps the visitor never sees.
17. **The demo's text field submits by GET.** The demo page is a `TemplateView`, which answers
    GET only.
18. **No fallback for browsers without `Element.checkVisibility()`.** Every current browser has
    it, and the browser tests run in Chromium only.
19. **A title or text of only whitespace counts as missing** (FR-004).
20. **Spec delta, approved by the orchestrating session holding the spec gate: what works while a
    step shows.** SC-005 and User Story 2's independent test said every control on the page works
    "during" the tour. Driver.js, which FR-008 makes the tour's drawing library, covers the page
    with an overlay while a step shows, and a click on the overlay closes the tour, so only the
    element the step is attached to can be used during it. Both now read: while a step shows,
    its attached element works and the rest of the page is reached by closing the tour in one
    action; after the tour ends or fails, every control works. This keeps Article XIII, which
    allows a change to the page only while a step is showing.
21. **No formatting hook touches the vendored Driver.js files.** The end-of-file and
    trailing-whitespace hooks rewrote them, and Article XII asks for the published release as
    it is. Their directory is excluded from pre-commit.
