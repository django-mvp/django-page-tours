"""URL configuration for the test suite."""

from django.urls import path

from tests import views

urlpatterns = [
    path("tour/", views.ClassTourView.as_view(), name="class-tour"),
    path("tour-again/", views.ClassTourView.as_view(), name="class-tour-again"),
    path("function-tour/", views.function_tour_view, name="function-tour"),
    path("markup-tour/", views.MarkupTourView.as_view(), name="markup-tour"),
    path(
        "translated-tour/", views.TranslatedTourView.as_view(), name="translated-tour"
    ),
    path("no-tour/", views.NoTourView.as_view(), name="no-tour"),
    path(
        "missing-class-tour/",
        views.MissingClassTourView.as_view(),
        name="missing-class-tour",
    ),
    path(
        "missing-function-tour/",
        views.missing_function_tour_view,
        name="missing-function-tour",
    ),
]
