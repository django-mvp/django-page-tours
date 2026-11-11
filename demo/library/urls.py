"""URL routes the library app ships, which a project includes."""

from django.urls import path

from demo.library.views import BookDetailView, BookListView, LoansView, borrow

urlpatterns = [
    path("books/", BookListView.as_view(), name="library-books"),
    path("book/", BookDetailView.as_view(), name="library-book"),
    path("loans/", LoansView.as_view(), name="library-loans"),
    path("book/borrow/", borrow, name="library-borrow"),
]
