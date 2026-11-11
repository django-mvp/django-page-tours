"""Declarations of a checklist: a panel on a page that lists what a visitor can do."""

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, ClassVar, Literal

from django.utils.functional import Promise
from django.utils.translation import pgettext_lazy

from page_tours.driver import Declaration, DriverObject
from page_tours.tours import Tour

Position = Literal["bottom-right", "bottom-left", "top-right", "top-left"]

# The defaults of the checklist's text, lazy so the active language applies when
# the checklist renders. The launcher's is plain, as Driver.js has it.
GET_STARTED_LABEL = pgettext_lazy("page checklist", "Get started")
CHECKLIST_PROGRESS_TEXT = pgettext_lazy("page checklist", "{{done}} of {{total}}")
LAUNCHER_PROGRESS_TEXT = "{{done}}/{{total}}"


@dataclass(frozen=True, kw_only=True)
class Offset(DriverObject):
    """How far the checklist sits from the corner of the window, as Driver.js takes it.

    The fields are named as Driver.js names them. A distance left as ``None`` is
    left out, so the value Driver.js falls back to applies.

    Args:
        x: The distance from the side of the window, in pixels.
        y: The distance from the top or bottom of the window, in pixels.
    """

    x: int | None = None
    y: int | None = None


@dataclass(frozen=True, kw_only=True)
class ChecklistItem(DriverObject):
    """One item of a checklist, as Driver.js takes it.

    The fields are named as Driver.js names them. An option left as ``None`` falls
    back to the value of the same name on the checklist. Title and description are
    passed to Driver.js as they are, and it writes them into the page as HTML.

    An item can start a tour, link to a page, or be ticked by the app or the
    visitor.

    Args:
        id: What the item is known by: the app reports it done under this id, and
            a browser remembers it was ticked under it.
        title: The heading of the item.
        description: The body of the item.
        tour: A tour that starts when the item is chosen. Its name, its version
            and ``PAGE_TOURS_OVERRIDES`` apply to it as they do to a tour on a
            page of its own. When the setting turns the tour off, the item is left
            out.
        href: The address the item opens when it is chosen.
        allowManualComplete: Whether the visitor can tick the item.
    """

    package_fields: ClassVar[frozenset[str]] = frozenset({"tour"})

    id: str
    title: str | Promise
    description: str | Promise | None = None
    tour: Tour | None = None
    href: str | None = None
    allowManualComplete: bool | None = None


@dataclass(frozen=True, kw_only=True)
class Checklist(Declaration):
    """A checklist on one page.

    A view or a context processor puts the checklist in its template context, and
    ``{{ checklist }}`` in the page's template renders it. Every checklist is
    recorded under its name when it is made, so the system checks can report a
    name declared twice or a ``PAGE_TOURS_OVERRIDES`` key that names nothing.

    The fields after ``version`` are Driver.js's checklist options, named and
    defaulting to the value Driver.js itself uses. Options that take a JavaScript
    function are not available. Driver.js writes the text into the page as HTML,
    so it is passed on as it is.

    What the app knows is done is reported with ``dataclasses.replace(checklist,
    completed=...)`` where the page is built. A checklist replaced through
    ``PAGE_TOURS_OVERRIDES`` plays with its own ``completed``.

    Args:
        name: The name the checklist is known by: a browser remembers what was
            ticked under it, and ``PAGE_TOURS_OVERRIDES`` changes the checklist by
            it. Plain text, never empty, and not shared with a tour or hints.
        items: The items, in order.
        version: A whole number of 1 or more. Raise it when the checklist has
            changed enough that what a browser ticked should be forgotten.
        title: The heading of the checklist, in the active language by default.
        description: The text under the heading.
        launcherText: The text of the launcher.
        completeTitle: The heading once every item is done.
        completeDescription: The text once every item is done.
        completeLauncherText: The text of the launcher once every item is done.
        progressText: The progress in the panel, in the active language by
            default. ``{{done}}`` and ``{{total}}`` stand for the counts.
        launcherProgressText: The progress on the launcher.
        position: Which corner of the window the checklist sits in.
        launcher: Whether a launcher is shown while the panel is closed.
        offset: How far the checklist sits from that corner.
        className: A class added to the checklist.
        allowManualComplete: Whether the visitor can tick any item.
        completed: The ids of the items the app reports done.

    Raises:
        ImproperlyConfigured: If ``name`` is not a string with something in it or
            ``version`` is not a whole number of 1 or more.
    """

    kind: ClassVar[str] = "checklist"
    content_field: ClassVar[str] = "items"

    items: Sequence[ChecklistItem]
    title: str | Promise = GET_STARTED_LABEL
    description: str | Promise | None = None
    launcherText: str | Promise | None = None
    completeTitle: str | Promise | None = None
    completeDescription: str | Promise | None = None
    completeLauncherText: str | Promise | None = None
    progressText: str | Promise = CHECKLIST_PROGRESS_TEXT
    launcherProgressText: str | Promise = LAUNCHER_PROGRESS_TEXT
    position: Position = "bottom-right"
    launcher: bool = True
    offset: Offset | None = None
    className: str = ""
    allowManualComplete: bool = False
    completed: Sequence[str] = ()

    package_fields = Declaration.package_fields | {"items"}

    def __post_init__(self):
        """Freeze the items and the completed ids and declare the checklist."""
        object.__setattr__(self, "items", tuple(self.items))
        object.__setattr__(self, "completed", tuple(self.completed))
        super().__post_init__()

    def as_driver(self) -> dict[str, Any]:
        """Convert the checklist to the form Driver.js takes.

        Returns:
            The options as ``DriverObject.as_driver()`` converts them, with the
            items, in order. An item with a tour carries the payload of the tour
            that plays under the tour's name, as the browser plays a tour on a
            page; an item whose tour ``PAGE_TOURS_OVERRIDES`` turns off is left
            out.

        Raises:
            ImproperlyConfigured: If the setting's entry for an item's tour is
                not valid or names a replacement that is not a tour.
        """
        driver = super().as_driver()
        items = []
        for item in self.items:
            converted = item.as_driver()
            if item.tour is not None:
                playing = item.tour.playing()
                if playing is None:
                    continue
                played, version = playing
                converted["tour"] = played.payload(item.tour.name, version)
            items.append(converted)
        driver["items"] = items
        return driver
