"""Settings for the demo project, a demonstration target that is never deployed."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-demo-project-only"

DEBUG = True

# The development server is reached over the network by hostname, not only at
# localhost. DEBUG auto-allows localhost and nothing else.
ALLOWED_HOSTS = ["*"]

# The development server speaks plain HTTP, and a browser discards a cookie
# marked Secure, which would leave every form post answered with 403.
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

INSTALLED_APPS = [
    "demo",
    "demo.library",
    "page_tours",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Reloads the browser on a change to a template, a stylesheet or Python. It
    # arrives with the shared development bundle, and its middleware removes
    # itself from the chain unless DEBUG is on.
    "django_browser_reload",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Last, because it rewrites the response body to insert its script tag.
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "demo.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "demo.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "demo.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS: list[dict] = []

STATIC_URL = "/static/"

# Classes for a few parts of a tour step, which the "Own look" page styles.
PAGE_TOURS_CLASSES = {
    "box": "demo-box",
    "previous": "demo-previous",
    "next": "demo-next",
    "done": "demo-done",
}

USE_TZ = True
USE_I18N = True
LANGUAGE_CODE = "en-us"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# The library app stands for a reusable app. Its files are untouched: the project
# replaces one of its tours and turns another off from here.
PAGE_TOURS_OVERRIDES = {
    "demo.library.views.BookDetailView": "demo.tours.book_tour",
    "demo.library.views.LoansView": None,
}
