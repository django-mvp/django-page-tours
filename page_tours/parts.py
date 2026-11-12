"""The parts of a tour, hints or checklist a site can style, and their classes."""

from django.apps import apps
from django.conf import settings


class TourParts:
    """The parts a site can style and the classes each one carries.

    The nine parts of a shown tour step, which a hint's popover and a checklist's
    panel also use, the beacon of a hint, and the launcher and an item of a
    checklist.

    Attributes:
        parts: Every part: the step's, in the order it shows them, then the
            beacon, the launcher and the item.
    """

    parts = (
        "box",
        "title",
        "text",
        "progress",
        "previous",
        "next",
        "done",
        "close",
        "highlight",
        "beacon",
        "launcher",
        "item",
    )

    @classmethod
    def name(cls, part):
        """Return the documented class name of a part.

        Args:
            part: One of ``parts``.

        Returns:
            The name, such as ``page-tour-box``.
        """
        return f"page-tour-{part}"

    @classmethod
    def sources(cls):
        """Yield where configured classes come from, most important first.

        The project's setting comes first, then each installed app that declares
        ``page_tour_classes``, in the order the apps are installed. Computed on
        every call, so a changed setting applies at once.

        Yields:
            A ``(source, mapping)`` pair: a description of where
            the mapping came from, and the mapping as found, which may be wrong.
        """
        yield (
            "the PAGE_TOURS_CLASSES setting",
            getattr(settings, "PAGE_TOURS_CLASSES", {}),
        )
        for config in apps.get_app_configs():
            if hasattr(config, "page_tour_classes"):
                yield (
                    f"the app '{config.label}'",
                    config.page_tour_classes,
                )

    @classmethod
    def classes(cls):
        """Return the class tokens every part carries.

        A part carries its documented name, then the classes of the first source
        holding a valid entry for it. A valid entry is a known part with a string
        value; an empty string is valid and adds no classes. Anything else is
        skipped, never raised, and is reported by the system checks.

        Returns:
            A dict from every part to its list of class tokens.
        """
        mappings = [
            mapping for source, mapping in cls.sources() if isinstance(mapping, dict)
        ]
        result = {}
        for part in cls.parts:
            configured = ""
            for mapping in mappings:
                if isinstance(mapping.get(part), str):
                    configured = mapping[part]
                    break
            result[part] = [cls.name(part), *configured.split()]
        return result
