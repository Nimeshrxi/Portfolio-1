# Nimesh Rai — Python Portfolio

A Python-first portfolio built with Django templates, Django REST Framework, and an optional Flask search microservice. The website has no JavaScript framework or image assets; the UI uses server-rendered templates and a single responsive CSS file.

## Architecture

- **Django**: server-rendered pages, admin, authentication middleware, contact form, and domain models.
- **Django REST Framework**: read-only project API, profile/skills endpoints, and validated contact endpoint.
- **Flask**: optional standalone search API (`/health`, `/api/search`). It reuses the same OOP search index.
- **Database**: SQLite for local development; PostgreSQL supported with `DATABASE_URL`.
- **Performance**: indexed model fields, bounded pagination, `select`/`prefetch` for skill relations, in-memory inverted-index search, short-lived caching, and no client-side framework hydration.

## Setup

Python 3.11+ recommended.

```bash
cd backend
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
copy .env.example .env   # PowerShell; use cp on macOS/Linux
python manage.py makemigrations portfolio
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_portfolio
python manage.py runserver
```

Open `http://127.0.0.1:8000/` for the portfolio and `/admin/` to manage profile, projects, skills, and contact messages. Create a Profile record and add projects through the admin. Public project APIs are read-only; only an authenticated staff member can edit portfolio content through Django admin.

## REST endpoints

- `GET /api/portfolio/projects/` — paginated published projects
- `GET /api/portfolio/projects/<slug>/` — one published project
- `GET /api/portfolio/profile/` — public profile
- `GET /api/portfolio/skills/` — grouped skills
- `GET /api/portfolio/search/?q=django&limit=10` — indexed project search
- `POST /api/portfolio/contact/` — JSON contact submission
- `POST /api/portfolio/contact/form/` — server-rendered contact form

## Optional Flask search service

Run from `backend/` in a separate terminal:

```bash
python -m search_service.app
```

It listens on `127.0.0.1:5001`. Example: `http://127.0.0.1:5001/api/search?q=python`. To load a JSON array of current project records, set `SEARCH_DATA_FILE` to its path before starting Flask. Django remains the source of truth for the website and main API.

## Tests and production

```bash
python manage.py check
python manage.py test portfolio
python manage.py collectstatic --noinput
```

For deployment, set a strong `DJANGO_SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, and a PostgreSQL `DATABASE_URL`. Terminate HTTPS at your platform/load balancer. Never commit `.env` files or production secrets.

## Algorithm note

`ProjectSearchIndex` builds an inverted index from tokens to document IDs. Search unions only matching posting lists, then ranks title matches above other matches. Build cost is proportional to total indexed tokens; query cost is proportional to query tokens plus candidate matches, rather than scanning every project's full text on each request. The index is rebuilt when the project dataset version changes.
