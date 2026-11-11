"""URL configuration for the test suite."""

from django.urls import path

from tests import views

urlpatterns = [
    path("navigation/", views.NavigationTourView.as_view(), name="navigation-tour"),
    path(
        "navigation-de/",
        views.GermanNavigationTourView.as_view(),
        name="german-navigation-tour",
    ),
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
    path("options/", views.OptionsTourView.as_view(), name="options-tour"),
    path("replay/", views.ReplayView.as_view(), name="replay"),
    path("replay-no-tour/", views.ReplayNoTourView.as_view(), name="replay-no-tour"),
    path(
        "replay-pointed-at/",
        views.ReplayPointedAtView.as_view(),
        name="replay-pointed-at",
    ),
    path(
        "replay-nothing-showable/",
        views.ReplayNothingShowableView.as_view(),
        name="replay-nothing",
    ),
    path("replay-twice/", views.ReplayTwiceView.as_view(), name="replay-twice"),
    path("on-request/", views.OnRequestView.as_view(), name="on-request"),
    path(
        "on-request-no-control/",
        views.OnRequestNoControlView.as_view(),
        name="on-request-no-control",
    ),
    path("versioned/", views.VersionedTourView.as_view(), name="versioned"),
    path(
        "versioned-two/",
        views.VersionedTourView.as_view(extra_context={"tour": views.VERSION_TWO}),
        name="versioned-two",
    ),
    path(
        "versioned-two-edited/",
        views.VersionedTourView.as_view(
            extra_context={"tour": views.VERSION_TWO_EDITED}
        ),
        name="versioned-two-edited",
    ),
    path(
        "on-request-two/",
        views.OnRequestView.as_view(
            extra_context={"tour": views.ON_REQUEST_VERSION_TWO}
        ),
        name="on-request-two",
    ),
    path("control-in-base/", views.ControlInBaseView.as_view(), name="control-in-base"),
    path(
        "control-in-base-no-tour/",
        views.ControlInBaseNoTourView.as_view(),
        name="control-in-base-no-tour",
    ),
    path("parts/", views.PartsTourView.as_view(), name="parts-tour"),
    path("style-before/", views.StyleBeforeView.as_view(), name="style-before"),
    path("style-after/", views.StyleAfterView.as_view(), name="style-after"),
    path("layer-before/", views.LayerBeforeView.as_view(), name="layer-before"),
    path("design-system/", views.DesignSystemView.as_view(), name="design-system"),
    path("not-deferred/", views.ScriptsNotDeferredView.as_view(), name="not-deferred"),
    path("tour-twice/", views.TourTwiceView.as_view(), name="tour-twice"),
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
    path("overridden/", views.OverriddenTourView.as_view(), name="overridden"),
    path(
        "overridden-again/",
        views.OverriddenTourView.as_view(),
        name="overridden-again",
    ),
    path("overridden-off/", views.OffTourView.as_view(), name="overridden-off"),
    path("untouched/", views.UntouchedTourView.as_view(), name="untouched"),
    path(
        "overridden-function/",
        views.overridden_function_view,
        name="overridden-function",
    ),
]
