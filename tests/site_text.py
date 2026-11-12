"""Running declarations under ``tests.settings_site_text``.

``PAGE_TOURS_TEXT`` is read when the package is imported, so a test of it runs
its declarations in a fresh interpreter started with those settings.
"""

import json
import os
import subprocess
import sys
import textwrap


def run_with_site_text(code):
    """Return what ``code`` prints as JSON, run under ``tests.settings_site_text``.

    Args:
        code: Python that prints one JSON value, with ``page_tours`` set up.

    Returns:
        The printed value.
    """
    script = "import django\ndjango.setup()\n" + textwrap.dedent(code)
    environment = os.environ | {"DJANGO_SETTINGS_MODULE": "tests.settings_site_text"}
    result = subprocess.run(  # noqa: S603 - runs this interpreter on our own code
        [sys.executable, "-c", script],
        capture_output=True,
        check=True,
        env=environment,
        text=True,
    )
    return json.loads(result.stdout)
