"""URL routes for the demo project."""

from django.contrib import admin
from django.urls import include, path

from demo.views import (
    FIRST_VERSION,
    NEW_VERSION,
    ChangedTourView,
    OnRequestView,
    OverviewView,
    OwnLookView,
    PlaysOnceView,
    TourView,
    function_view,
)

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("tour/", TourView.as_view(), name="tour"),
    path("plays-once/", PlaysOnceView.as_view(), name="plays-once"),
    path("on-request/", OnRequestView.as_view(), name="on-request"),
    path(
        "changed-tour/",
        ChangedTourView.as_view(tour=FIRST_VERSION),
        name="changed-tour",
    ),
    path(
        "changed-tour/new-version/",
        ChangedTourView.as_view(tour=NEW_VERSION),
        name="changed-tour-new-version",
    ),
    # A reusable app ships its URLs and the project includes them.
    path("library/", include("demo.library.urls")),
    path("own-look/", OwnLookView.as_view(), name="own-look"),
    path("function-view/", function_view, name="function-view"),
    path("admin/", admin.site.urls),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
