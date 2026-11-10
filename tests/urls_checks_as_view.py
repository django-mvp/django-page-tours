"""A URL configuration whose one tour is given through ``as_view``."""

from django.urls import path

from tests import views

urlpatterns = [
    path("given/", views.OverriddenTourSubclassView.as_view(tour=views.OWN_TOUR)),
]
