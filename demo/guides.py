"""The demo project's hints and its checklist."""

from dataclasses import replace

from page_tours import (
    Beacon,
    Checklist,
    ChecklistItem,
    Hint,
    Hints,
    Tour,
    TourStep,
)

REPORT_HINTS = Hints(
    name="demo.report",
    beacon=Beacon(side="right", align="start"),
    hints=[
        Hint(
            element="#report-export",
            title="Export the report",
            description="Download this quarter's figures as a spreadsheet.",
        ),
        Hint(
            element="#report-summary",
            id="summary",
            title="Written for you",
            description="This paragraph is written from the quarter's figures.",
            side="bottom",
            beacon=Beacon(side="left", align="center"),
        ),
        Hint(
            element="#report-figures",
            title="The figures",
            description="Each row is one month. <strong>Bold</strong> rows beat their target.",
            buttonText="Understood",
        ),
        Hint(
            element="#report-share",
            title="Share it",
            description="Anyone with the link can read the report, but not change it.",
            beacon=Beacon(animate=False, className="demo-quiet-beacon"),
        ),
    ],
)

REPORT_TOUR = Tour(
    name="demo.report-tour",
    autoplay=False,
    steps=[
        TourStep(
            title="The hints step aside",
            description="While a tour plays, the hints' beacons are hidden.",
        ),
        TourStep(
            title="And come back",
            description="When the tour ends, the beacons return.",
            element="#report-figures",
        ),
    ],
)

# The tour the checklist's first item starts. It is a Tour like any page's,
# declared the same way.
WELCOME_TOUR = Tour(
    name="demo.welcome",
    autoplay=False,
    steps=[
        TourStep(
            title="Welcome",
            description="This is the demo project of Django Page Tours.",
        ),
        TourStep(
            title="Every page",
            description="Each link up here shows one thing the package does.",
            element="[aria-label='Demo pages']",
            side="bottom",
        ),
        TourStep(
            title="Your checklist",
            description="When this tour ends, your checklist opens again with this item ticked.",
        ),
    ],
    showProgress=True,
)

ONBOARDING = Checklist(
    name="demo.onboarding",
    title="Get to know the package",
    description="Four things to try in this demo.",
    completeTitle="All done",
    completeDescription="You have seen what tours, hints and checklists do.",
    completeLauncherText="All done",
    items=[
        ChecklistItem(
            id="welcome",
            title="Take the welcome tour",
            description="A short tour of this demo.",
            tour=WELCOME_TOUR,
        ),
        ChecklistItem(
            id="hints",
            title="Open the hints page",
            description="Beacons you open in any order.",
            href="/hints/",
        ),
        ChecklistItem(
            id="borrow",
            title="Borrow a book",
            description="Ticked by the app once you have borrowed one.",
        ),
        ChecklistItem(
            id="docs",
            title="Read Driver.js's checklist guide",
            description="Tick it yourself when you have.",
            href="https://driverjs.com/docs/checklists",
            allowManualComplete=True,
        ),
    ],
)


def onboarding(request):
    """Put the checklist on every page, with what the app knows is done.

    Args:
        request: The request being rendered.

    Returns:
        The checklist under ``checklist``, with the borrow item done once the
        visitor has borrowed a book.
    """
    done = ("borrow",) if request.session.get("borrowed") else ()
    return {"checklist": replace(ONBOARDING, completed=done)}
