"""A URL configuration of views that declare tours, for the check tests."""

from django.urls import include, path

from tests import views

urlpatterns = [
    path("untouched/", views.UntouchedTourView.as_view()),
    path("subclass/", views.OverriddenTourSubclassView.as_view()),
    path("function/", views.overridden_function_view),
    path("included/", include([path("off/", views.OffTourView.as_view())])),
]
