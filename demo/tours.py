"""Tours the demo project uses in place of an installed app's own."""

from demo.library.views import BOOK_TOUR
from page_tours import Tour, TourStep

# The library app's first step, then its second one reworded for this project.
book_tour = Tour(
    name="demo.book",
    steps=(
        *BOOK_TOUR.steps[:1],
        TourStep(
            title="Borrow it here",
            description="This library lends each book for a week. Press the button.",
            element="#library-borrow",
        ),
    ),
)
