# ADR 0004 — A project changes an installed app's tour by its name

**Status:** superseded by ADR 0006

## Decision

A project replaces or turns off a tour declared on a view of an installed app with the setting
`PAGE_TOURS_OVERRIDES`. Each key is a tour's name, the dotted path of the view that declares it
(ADR 0002). Each value is the dotted path of a replacement `Tour`, or `None` to turn the tour off.

- `Tour.for_page` applies the setting after it finds the declared tour, so a replaced tour keeps
  its name and the seen state stored under it.
- A replacement plays at the app tour's version plus its own, less one. A replacement left at
  version 1 plays at the app tour's version, and raising it shows the replacement again.
- Every entry is resolved when the project starts, and the system check `page_tours.W002` warns
  about a key that no routed view declares a tour under.

This makes a tour's name part of what an app promises the projects that install it. Renaming or
moving a view that declares a tour, or raising that tour's version, is a change those projects
see.

## Why

The project installing an app needs a say over the app's tours without editing the app,
subclassing its views or routing to views of its own.

- Naming the tour by its declaring view needs nothing from the app's author. A name the author
  gives each tour would be a setting every app has to add and keep stable.
- A setting with Django's `MIGRATION_MODULES` shape is where a developer already changes what the
  project takes from its installed apps. A registry the project fills from its own code needs a
  place and an order to be called from, and state a test has to reset.
- The value is a dotted path, not a tour, because a replacement that reuses the app's steps
  imports the app's views, which settings load too early to do.
- The browser compares the version a page emits. Emitting the replacement's own version would
  play it once for everyone who saw an app tour above version 1. Emitting the app's version
  would leave the project no way to show its replacement again. Counting on from the app's
  version keeps both, at the cost that an app release raising its own version shows the
  replacement again once.

## Revisit if

- An app needs to rename or move a view without breaking the projects that changed its tour.
- A project needs to change one step of an app's tour rather than the whole tour.
