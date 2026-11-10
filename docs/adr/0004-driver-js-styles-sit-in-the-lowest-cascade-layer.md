# ADR 0004 — Driver.js's stylesheet sits in the lowest cascade layer

**Status:** accepted

## Decision

The package links one stylesheet of its own, `page_tours/page-tours.css`. Its only content imports
Driver.js's stylesheet, unchanged, into a cascade layer named `page-tours`. The starter script
moves that link to the start of the page's `<head>` before a tour plays, so the `page-tours` layer
is declared before any other and is the lowest layer on the page.

## Why

A site's own rules have to beat Driver.js's defaults wherever the site links its stylesheet, and a
site on a framework that puts its classes in cascade layers has to see those classes take effect.

- Rules outside any layer beat every layered rule, whatever their specificity or order. Putting
  Driver.js's rules in a layer is the only way to put them under a site's ordinary rules without
  editing Driver.js's stylesheet.
- Between layers, the one declared first loses. A layer declared after a framework's would outrank
  its classes, so the package's link is moved to the start of the head rather than left wherever
  the template tag sits.
- An inline `<style>` holding the import would do the same without a file of the package's own,
  and is blocked by a strict content security policy. A linked file is not.
- Driver.js's stylesheet stays byte-identical to its release, so moving to a new Driver.js release
  is still a matter of replacing the shipped files.

## Consequences

- A site rule written against a bare element, such as `button { … }`, and a framework's layered
  reset now reach the tour's parts as they reach the rest of the page. Styling the documented
  names settles any of it.
- The package's only style rules are still Driver.js's. `page-tours.css` holds an import and
  nothing else.
- With JavaScript off nothing is moved, and no tour plays.

## Revisit if

- Browsers accept a layer on a `<link>` element, which would remove the one-line file.
- A Driver.js release ships its own stylesheet in a layer.
