"""URL configuration for the test suite."""

from django.urls import path

from tests import views

urlpatterns = [
    path("navigation/", views.NavigationTourView.as_view(), name="navigation-tour"),
    path("missing-first/", views.MissingFirstTourView.as_view(), name="missing-first"),
    path(
        "missing-middle/", views.MissingMiddleTourView.as_view(), name="missing-middle"
    ),
    path("hidden-middle/", views.HiddenMiddleTourView.as_view(), name="hidden-middle"),
    path("invalid-selector/", views.InvalidSelectorTourView.as_view(), name="invalid"),
    path("nothing-showable/", views.NothingShowableTourView.as_view(), name="nothing"),
    path("twins/", views.TwinTourView.as_view(), name="twins"),
    path("fragile/", views.FragileTourView.as_view(), name="fragile"),
    path("with-tour-bare/", views.BareTourView.as_view(), name="bare-with-tour"),
    path(
        "without-tour-bare/",
        views.NoTourControlsView.as_view(),
        name="bare-without-tour",
    ),
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
