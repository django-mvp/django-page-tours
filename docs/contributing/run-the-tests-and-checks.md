# Run the tests and checks

Each command below runs the same check as CI.

## The test suite

```bash
uv run pytest
```

The suite includes the demo project's pages.

## Linting, formatting and type checks

```bash
uv run pre-commit run --all-files
```

This runs ruff, mypy and deptry. Run it rather than a bare `ruff check .`: the hook configuration
excludes paths and runs hooks that a bare call does not.

## The documentation

```bash
uv run --group docs sphinx-build -E -W -b html docs docs/_build
```

`-W` treats a warning as an error, so a page missing from the contents or a broken link fails
the build. Run it this way before opening a pull request.

## Everything at once

```bash
uv run invoke check
```
