# Nimesh Rai Portfolio — Python Edition

A Python-first, server-rendered portfolio for a Python Backend Developer. The experience uses a cinematic black-and-red visual system inspired by comic-book web-slinging: lightweight cursor-reactive web lines, click-triggered web-shooter strands, floating project cards, and subtle pointer-directed card tilt. No external image assets, frontend framework, animation library, or third-party font is required. A small vanilla JavaScript file is used only for browser interactions; the application and backend remain Python-first.

## Stack

- **Django**: server-rendered portfolio, admin, domain models, and contact form.
- **Django REST Framework**: published-project, profile, skills, search, and contact APIs.
- **Flask**: optional standalone search microservice sharing the OOP search index.
- **Database**: SQLite for local development; PostgreSQL supported through `DATABASE_URL`.
- **Performance and UX**: indexed models, bounded API pagination, prefetched skill relationships, in-process inverted-index search, no frontend framework hydration, a capped canvas render rate, capped device-pixel ratio, and reduced-motion support.

## Run locally

Python 3.11+ recommended.

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_portfolio
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Use `/admin/` to manage profile, projects, skills, and contact messages. Create or update your Profile record and verify your email, GitHub, and LinkedIn URLs before publishing. Public project APIs are read-only; portfolio content changes belong to staff users through Django Admin.

## REST endpoints

- `GET /api/portfolio/projects/` — paginated published projects
- `GET /api/portfolio/projects/<slug>/` — one published project
- `GET /api/portfolio/profile/` — public profile
- `GET /api/portfolio/skills/` — grouped skills
- `GET /api/portfolio/search/?q=django&limit=10` — indexed project search
- `POST /api/portfolio/contact/` — JSON contact submission
- `POST /api/portfolio/contact/form/` — server-rendered contact form

## Optional Flask search service

Run from `backend/` in another terminal:

```powershell
python -m search_service.app
```

It listens on `127.0.0.1:5001`; test it at `/health` or `/api/search?q=python`. Set `SEARCH_DATA_FILE` to a JSON array of project records if you want Flask to load project data. Django remains the primary source of truth.

## Verification

```powershell
python manage.py check
python manage.py test portfolio
python manage.py collectstatic --noinput
```

Before deployment, set a strong unique `DJANGO_SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, HTTPS `CSRF_TRUSTED_ORIGINS`, a PostgreSQL `DATABASE_URL`, and real SMTP credentials if contact email delivery is required. Never commit `.env` or production secrets. Configure your hosting platform to serve static files and terminate HTTPS. Review `python manage.py check --deploy` before going live.

## Search algorithm

`ProjectSearchIndex` builds an inverted index from normalized tokens to matching document IDs. Queries inspect only posting lists for query tokens, then rank title matches above secondary text matches. Search work scales with query-token count and matching candidates instead of rescanning every project's full text for every query. The index is rebuilt when the published-project dataset version changes.

## Motion and accessibility

The decorative canvas runs only for fine-pointer devices, caps rendering to approximately 30 FPS and device pixel ratio 1.5, stops drawing while idle, and is disabled for `prefers-reduced-motion`. All navigation, project details, and contact functionality remain usable if the canvas is unavailable.
