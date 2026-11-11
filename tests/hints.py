"""Hints the tests render and the modules that declare them for the checks."""

from page_tours import Beacon, Hint, Hints, Tour, TourStep

REPORT_HINTS = Hints(
    name="tests.hints.report",
    hints=[
        Hint(
            element="#first",
            id="first",
            title="First",
            description="Body one.",
            side="bottom",
        ),
        Hint(element="#second", title="Second", description="Body two."),
    ],
)
REPLACEMENT_HINTS = Hints(
    name="tests.hints.replacement",
    hints=[Hint(element="#other", title="Other", description="Instead.")],
)
REPLACEMENT_HINTS_VERSION_TWO = Hints(
    name="tests.hints.replacement-two",
    version=2,
    hints=[Hint(element="#other", title="Other", description="Instead.")],
)
TOUR_AS_REPLACEMENT = Tour(
    name="tests.hints.tour-replacement",
    steps=[TourStep(title="Tour", description="Not hints.")],
)
BEACON = Beacon(side="left", offsetX=4)
