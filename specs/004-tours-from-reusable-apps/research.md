# Research — FS-004 Tours shipped by reusable apps

## Assumptions checked

Run on `main` at `b32f9f7` before the specification was written.

- **A tour declared in another installed app plays in the project.** The demo project in `demo/`
  is an installed app separate from `page_tours`, and its views declare tours the way a reusable
  app's would. `uv run pytest tests/test_demo.py`: 22 passed, including its tour pages. Holds.
- **A project's subclass of an app's view keeps the app's tour name.** A subclass of
  `demo.views.OnRequestView` that sets no tour of its own is named
  `demo.views.OnRequestView` by `tour_id`. Holds, so scenario 6 can be met by naming the app's
  view.
- **A mistaken tour is refused when declared.** `Tour(steps=[])` and a `TourStep` with an empty
  title raise `ImproperlyConfigured` at construction (`page_tours/tours.py`). Holds, so FR-010
  follows from the existing rule when the replacement is built at start-up.
