"""URL routes for the demo project."""

from django.contrib import admin
from django.urls import include, path

from demo.views import OverviewView

urlpatterns = [
    path("", OverviewView.as_view(), name="overview"),
    path("admin/", admin.site.urls),
    # The endpoint an open page holds to hear that something on disk changed.
    path("__reload__/", include("django_browser_reload.urls")),
]
