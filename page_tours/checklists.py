"""Declarations of a checklist, mirroring Driver.js's checklists.

A checklist is a "Get started" widget in a corner of the page. Each item is one
thing a visitor is asked to do: take a tour, follow a link, or do something in
the app. An item is ticked when the visitor finishes its tour, follows its link,
ticks it themselves, or the view says it is done. The browser remembers what is
ticked until the checklist's version is raised.

See https://driverjs.com/docs/checklists.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import ClassVar, Literal

from django.utils.functional import Promise
from django.utils.translation import pgettext_lazy

from page_tours.driver import DriverObject, Guide
from page_tours.tours import Tour

Position = Literal["bottom-right", "bottom-left", "top-right", "top-left"]

# The default heading of a checklist: lazy, so the active language applies.
GET_STARTED_LABEL = pgettext_lazy("page checklist", "Get started")
PROGRESS_TEXT = pgettext_lazy("page checklist", "{{done}} of {{total}}")
LAUNCHER_PROGRESS_TEXT = "{{done}}/{{total}}"


@dataclass(frozen=True, kw_only=True)
class Offset(DriverObject):
    """How far the checklist sits from the edges of the screen.

    Args:
        x: Pixels from the left or right edge.
        y: Pixels from the top or bottom edge.
    """

    x: int | None = None
    y: int | None = None


@dataclass(frozen=True, kw_only=True)
class ChecklistItem(DriverObject):
    """One item of a checklist.

    Give an item a ``tour`` to start, an ``href`` to follow, or neither, for
    something done in the app that the view reports in the checklist's
    ``completed``.

    Args:
        id: What the item's tick is remembered under. Keep it when the item is
            reworded or moved.
        title: What the visitor is asked to do.
        description: A line more about it.
        tour: The tour the item starts. The item is ticked when the visitor
            finishes it, and the tour then counts as seen.
        href: The link the item follows. It is ticked when followed.
        allowManualComplete: Whether the visitor can tick and untick this item
            themselves, in place of the checklist's setting.
    """

    id: str
    title: str | Promise
    description: str | Promise | None = None
    tour: Tour | None = None
    href: str | None = None
    allowManualComplete: bool | None = None


@dataclass(frozen=True, kw_only=True)
class Checklist(Guide):
    """A checklist: Driver.js's checklist configuration, as a Python class.

    A view puts it in its template context, and ``{{ checklist }}`` renders it.
    The checklist's ``name`` is Driver.js's ``id``. The fields after ``version``
    are Driver.js's options, named and defaulted as in Driver.js 1.11.0. Options
    that take a JavaScript function are not available. In place of an item's
    ``completeWhen``, the view sets ``completed`` from what the app knows::

        dataclasses.replace(ONBOARDING, completed=done_ids_for(request.user))

    Args:
        items: The items, in the order they are listed.
        title: The heading of the panel.
        description: A line under the heading.
        launcherText: The text of the button that opens the panel. Defaults to
            the title.
        completeTitle: The heading once every item is ticked.
        completeDescription: The line under it once every item is ticked.
        completeLauncherText: The launcher's text once every item is ticked.
        progressText: The panel's progress, with ``{{done}}``, ``{{total}}``,
            ``{{remaining}}`` and ``{{percent}}``.
        launcherProgressText: The launcher's progress, with the same words.
        position: The corner of the screen the checklist sits in.
        launcher: Whether the checklist shows its own launcher. Without one, a
            control with ``data-page-checklist-toggle`` opens it.
        offset: How far it sits from the edges of the screen.
        className: A class added to the checklist.
        allowManualComplete: Whether a visitor can tick and untick items.
        completed: The ids of the items that are already done.
    """

    items: Sequence[ChecklistItem]
    title: str | Promise = GET_STARTED_LABEL
    description: str | Promise | None = None
    launcherText: str | Promise | None = None
    completeTitle: str | Promise | None = None
    completeDescription: str | Promise | None = None
    completeLauncherText: str | Promise | None = None
    progressText: str | Promise = PROGRESS_TEXT
    launcherProgressText: str | Promise = LAUNCHER_PROGRESS_TEXT
    position: Position = "bottom-right"
    launcher: bool = True
    offset: Offset | None = None
    className: str = ""
    allowManualComplete: bool = False
    completed: tuple[str, ...] = ()

    kind: ClassVar[str] = "checklist"

    def __post_init__(self):
        """Freeze the items and record the checklist under its name."""
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "completed", tuple(self.completed))
        super().__post_init__()
