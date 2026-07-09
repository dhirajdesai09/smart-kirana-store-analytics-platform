# StorePulse

StorePulse is a production-style full-stack analytics platform for small grocery and kirana shop owners. It combines inventory management, POS sales, Pandas-powered BI, demand forecasting, festival analysis, alerts, and exportable reports in a SaaS-style dashboard.

## Stack

- Backend: Python, Django, Django REST Framework, JWT auth
- Frontend: React, Vite, Axios, React Router, Recharts, lucide-react
- Database: MySQL by default, `DATABASE_URL` ready for managed deployment
- Analytics: Pandas, NumPy, optional scikit-learn
- Reports: CSV, Excel, PDF
- Deployment: Docker Compose locally, Render/Railway/Vercel friendly

## Project Structure

```text
backend/
  apps/
    accounts/          stores, profiles, staff roles
    inventory/         categories, suppliers, products, stock logs, demo seed
    sales/             invoices, sale items, inventory movement
    analytics_engine/  Pandas BI, basket analysis, forecasting, alerts
    reports/           report history and exports
  storepulse/          settings, urls, ASGI/WSGI
frontend/
  src/
    pages/             dashboard, inventory, sales, analytics, reports, settings
    components/        reusable SaaS UI pieces
docs/API.md
docker-compose.yml
```

## Documentation

- [Run Guide](docs/RUN_GUIDE.md): verified MySQL, backend, frontend, Docker, and troubleshooting steps
- [Project Documentation](docs/PROJECT_DOCUMENTATION.md): architecture, workflows, APIs, and all 20 database tables
- [API Documentation](docs/API.md)
- [Viva And Interview Questions](docs/VIVA_QUESTIONS.md): 60 answered project and database questions
- [Study Notes](docs/STUDY_NOTES.md): revision notes for functionality, database design, analytics, and demonstrations

## Run With Docker

```bash
docker compose up --build
```

Then run the demo seed in another terminal:

```bash
docker compose exec backend python manage.py seed_demo
```

Open:

- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/api/docs/`

Demo login after seeding:

- Email: `owner@storepulse.local`
- Password: `Demo@12345`

## Local Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

For quick SQLite development, set `DB_ENGINE=sqlite` in `backend/.env`.

## Local Frontend

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_URL=http://localhost:8000/api` if the frontend is not using the Vite proxy.

## Deployment Notes

- Backend on Render/Railway: set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS`, and `DATABASE_URL`.
- Frontend on Vercel/Netlify: set `VITE_API_URL` to the deployed backend API URL.
- Database: MySQL is the first-class target. Managed MySQL via Railway/PlanetScale/Aiven works through `DATABASE_URL`.
- Production command: `python manage.py migrate && gunicorn storepulse.wsgi:application --bind 0.0.0.0:$PORT`

## Resume Highlights

- Normalized relational schema with store scoping and role-based access.
- Nested sales APIs that generate invoices, compute GST-ready totals, and update inventory logs atomically.
- Pandas analytics using groupby, merge, pivot tables, moving averages, and basket-pair analysis.
- Forecasting for next-week demand and stock shortage risk.
- India-focused festival and seasonal analytics.
- SaaS dashboard with responsive React UI, protected routes, loading/error states, charts, and exports.
