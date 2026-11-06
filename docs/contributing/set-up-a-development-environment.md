# Set up a development environment

You need [uv](https://docs.astral.sh/uv/) and Git. uv installs the right Python for you.

## Get the code and its dependencies

```bash
git clone https://github.com/django-mvp/django-page-tours.git
cd django-page-tours
uv sync
uv run pre-commit install
```

`uv sync` installs the package with its development tools. `pre-commit install` runs the linters
on every commit.

## Run the demo project

The repository carries a demo project in `demo/`. It is not part of the package. It has a page
for each feature, so you can see the package working in a browser while you change it.

```bash
uv run python manage.py migrate
uv run python manage.py seed_demo
uv run python manage.py runserver
```

Open <http://localhost:8000/>. `seed_demo` creates three accounts, `regular.user@example.com`,
`staff.user@example.com` and `super.user@example.com`, all with the password `password`. The
staff and superuser accounts can sign in to the admin at `/admin/`. The page reloads by itself
when you change a template or Python file.
