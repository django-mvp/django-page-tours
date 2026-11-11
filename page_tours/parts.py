"""The parts of a tour step a site can style, and the classes each one carries."""

from django.apps import apps
from django.conf import settings
from django.utils.translation import gettext_lazy


class TourParts:
    """The nine parts of a shown tour step and the classes each one carries.

    Attributes:
        parts: Every part, in the order the step shows them.
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
            A ``(source, mapping)`` pair: a translatable description of where
            the mapping came from, and the mapping as found, which may be wrong.
        """
        yield (
            gettext_lazy("the PAGE_TOURS_CLASSES setting"),
            getattr(settings, "PAGE_TOURS_CLASSES", {}),
        )
        for config in apps.get_app_configs():
            if hasattr(config, "page_tour_classes"):
                yield (
                    gettext_lazy("the app '%(label)s'") % {"label": config.label},
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
