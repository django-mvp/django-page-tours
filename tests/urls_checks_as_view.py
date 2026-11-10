"""A URL configuration whose one tour is given through ``as_view``."""

from django.urls import path

from tests import views

urlpatterns = [
    path(
        "given/",
        views.OverriddenTourView.as_view(extra_context={"tour": views.OWN_TOUR}),
    ),
]
