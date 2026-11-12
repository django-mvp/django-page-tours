"""Django settings for testing django-page-tours with PAGE_TOURS_TEXT set."""

from tests.settings import *  # noqa: F403

PAGE_TOURS_TEXT = {
    "tour": {"nextBtnText": "Site next", "progressText": "Site progress"},
    "hint": {"buttonText": "Site button"},
    "checklist": {"title": "Site title"},
}
