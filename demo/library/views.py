"""The library app's pages, each declaring its own tour.

The app names each tour ``"library.<tour>"``, after its app label, so its names
cannot clash with the tours of the project or of another app.
"""

from django.views.generic import TemplateView

from page_tours import Tour, TourStep

BOOK_LIST_TOUR = Tour(
    name="library.book-list",
    steps=[
        TourStep(
            title="The library's books",
            text="Every book the library holds is listed here.",
            element="#library-books",
        ),
        TourStep(
            title="Open a book",
            text="Choose a title to see its page.",
            element="#library-first-book",
        ),
    ],
)


class BookListView(TemplateView):
    """The books the library holds."""

    template_name = "library/book_list.html"
    extra_context = {"tour": BOOK_LIST_TOUR}


BOOK_TOUR = Tour(
    name="library.book",
    steps=[
        TourStep(
            title="A book",
            text="This page shows one book.",
            element="#library-book-title",
        ),
        TourStep(
            title="Borrow it",
            text="Press the button to borrow the book.",
            element="#library-borrow",
        ),
    ],
)


class BookDetailView(TemplateView):
    """One book of the library."""

    template_name = "library/book_detail.html"
    extra_context = {"tour": BOOK_TOUR}


LOANS_TOUR = Tour(
    name="library.loans",
    steps=[
        TourStep(
            title="Your loans",
            text="The books you have borrowed are listed here.",
            element="#library-loans",
        ),
    ],
)


class LoansView(TemplateView):
    """The books a reader has borrowed."""

    template_name = "library/loans.html"
    extra_context = {"tour": LOANS_TOUR}
