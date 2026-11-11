"""Checklists the tests render and the modules that declare them for the checks."""

from page_tours import Checklist, ChecklistItem, Tour, TourStep

WELCOME_TOUR = Tour(
    name="tests.checklists.welcome",
    version=2,
    autoplay=False,
    steps=[TourStep(title="Welcome", description="Look around.")],
)
REPLACEMENT_TOUR = Tour(
    name="tests.checklists.welcome-replacement",
    version=4,
    steps=[TourStep(title="Instead", description="Another look.")],
)
ONBOARDING = Checklist(
    name="tests.checklists.onboarding",
    items=[
        ChecklistItem(id="welcome", title="Take the tour", tour=WELCOME_TOUR),
        ChecklistItem(id="hints", title="Read the hints", href="/hints/"),
        ChecklistItem(id="borrow", title="Borrow a book"),
    ],
)
REPLACEMENT_CHECKLIST = Checklist(
    name="tests.checklists.replacement",
    version=3,
    items=[ChecklistItem(id="other", title="Another item")],
    completed=["other"],
)
