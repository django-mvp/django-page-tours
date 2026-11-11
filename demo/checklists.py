"""The demo project's onboarding checklist and the tour its first item starts."""

from dataclasses import replace

from page_tours import Checklist, ChecklistItem, Tour, TourStep

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
            description=(
                "When this tour ends, your checklist opens again with this item ticked."
            ),
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
    """Put the onboarding checklist in the context of every page.

    Args:
        request: The request being answered.

    Returns:
        The checklist under ``checklist``, with the borrow item reported done once
        the visitor has borrowed a book.
    """
    done = ("borrow",) if request.session.get("borrowed") else ()
    return {"checklist": replace(ONBOARDING, completed=done)}
