"""URL routes for the demo project."""

from django.contrib import admin
from django.urls import include, path

from demo.views import OnRequestView, OverviewView, PlaysOnceView, TourView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("tour/", TourView.as_view(), name="tour"),
    path("plays-once/", PlaysOnceView.as_view(), name="plays-once"),
    path("on-request/", OnRequestView.as_view(), name="on-request"),
    path("admin/", admin.site.urls),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
