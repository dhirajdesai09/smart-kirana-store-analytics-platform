# StorePulse Run Guide

This guide explains how to run the MySQL-backed StorePulse project locally for
demo, study, and development. Commands were verified on July 4, 2026.

Current project location:

```text
/Users/dhirajjangondadesai/Developer/2026-05-24/smart-kirana-store-analytics-platform-full
```

## Current Local Demo URLs

When both servers are running:

- Frontend: `http://127.0.0.1:5173/`
- Backend API: `http://127.0.0.1:8000/api/`
- API Docs: `http://127.0.0.1:8000/api/docs/`

Demo login after seeding:

- Email: `owner@storepulse.local`
- Password: `Demo@12345`

## Prerequisites

Install these tools:

- Python 3.12 or newer
- Node.js and npm
- MySQL 8 or newer for the recommended setup
- Docker Desktop, optional

Check installed versions:

```bash
python3 --version
node --version
npm --version
mysql --version
```

## Recommended Local Run With MySQL

### 1. Confirm MySQL Is Running

On macOS with Homebrew:

```bash
brew services list
brew services start mysql
```

Confirm the server accepts connections:

```bash
mysql -u root -p
```

### 2. Create the Database and Application User

Run the following inside the MySQL prompt:

```sql
CREATE DATABASE IF NOT EXISTS storepulse
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'storepulse'@'localhost'
  IDENTIFIED BY 'StorePulse@123';
CREATE USER IF NOT EXISTS 'storepulse'@'127.0.0.1'
  IDENTIFIED BY 'StorePulse@123';

ALTER USER 'storepulse'@'localhost'
  IDENTIFIED BY 'StorePulse@123';
ALTER USER 'storepulse'@'127.0.0.1'
  IDENTIFIED BY 'StorePulse@123';

GRANT ALL PRIVILEGES ON storepulse.* TO 'storepulse'@'localhost';
GRANT ALL PRIVILEGES ON storepulse.* TO 'storepulse'@'127.0.0.1';
FLUSH PRIVILEGES;
EXIT;
```

Test the application account:

```bash
mysql -h 127.0.0.1 -u storepulse -p storepulse
```

Enter `StorePulse@123` when prompted.

### 3. Configure and Start the Backend

```bash
cd /Users/dhirajjangondadesai/Developer/2026-05-24/smart-kirana-store-analytics-platform-full/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create or update `backend/.env`:

```env
DJANGO_SECRET_KEY=storepulse-local-dev-key-2026-change-before-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DB_ENGINE=mysql
MYSQL_DATABASE=storepulse
MYSQL_USER=storepulse
MYSQL_PASSWORD=StorePulse@123
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
DJANGO_TIME_ZONE=Asia/Kolkata
```

Create tables and demo data:

```bash
python manage.py check
python manage.py migrate
python manage.py seed_demo
```

Verify that Django is connected to MySQL:

```bash
python manage.py shell -c "from django.db import connection; print(connection.vendor, connection.settings_dict['NAME'])"
```

Expected output:

```text
mysql storepulse
```

Start the backend:

```bash
python manage.py runserver 127.0.0.1:8000
```

Keep this terminal open.

### 4. Configure and Start the Frontend

Open a second terminal:

```bash
cd /Users/dhirajjangondadesai/Developer/2026-05-24/smart-kirana-store-analytics-platform-full/frontend
npm install
npm run dev -- --host 127.0.0.1
```

The frontend defaults to `http://127.0.0.1:8000/api`. To override it, create
`frontend/.env`:

```env
VITE_API_URL=http://127.0.0.1:8000/api
```

Open `http://127.0.0.1:5173/` and sign in with the demo account.

### 5. Verify the Complete Setup

```bash
curl -I http://127.0.0.1:5173/
curl -I http://127.0.0.1:8000/api/docs/
mysql -h 127.0.0.1 -u storepulse -p -e "USE storepulse; SHOW TABLES;"
```

The database should contain 20 tables after migrations.

## Fastest Local Run With SQLite

SQLite is an optional fallback for quick development. It is not the active
database for the configured project.

### 1. Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:

```env
DJANGO_SECRET_KEY=storepulse-local-dev-key-2026-change-before-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DB_ENGINE=sqlite
DJANGO_TIME_ZONE=Asia/Kolkata
```

Run migrations and seed data:

```bash
python manage.py migrate
python manage.py seed_demo
```

Start backend:

```bash
python manage.py runserver 127.0.0.1:8000
```

If your environment blocks Django runserver, use:

```bash
gunicorn storepulse.wsgi:application --bind 127.0.0.1:8000 --workers 1
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open `http://127.0.0.1:5173/`.

## MySQL Local Run

The complete recommended MySQL procedure is at the beginning of this guide.
This shorter reference is useful after initial setup.

Create a MySQL database and user:

```sql
CREATE DATABASE IF NOT EXISTS storepulse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'storepulse'@'localhost' IDENTIFIED BY 'StorePulse@123';
CREATE USER IF NOT EXISTS 'storepulse'@'127.0.0.1' IDENTIFIED BY 'StorePulse@123';
GRANT ALL PRIVILEGES ON storepulse.* TO 'storepulse'@'localhost';
GRANT ALL PRIVILEGES ON storepulse.* TO 'storepulse'@'127.0.0.1';
FLUSH PRIVILEGES;
```

Update `backend/.env`:

```env
DJANGO_SECRET_KEY=storepulse-local-dev-key-2026-change-before-production
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DB_ENGINE=mysql
MYSQL_DATABASE=storepulse
MYSQL_USER=storepulse
MYSQL_PASSWORD=StorePulse@123
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
DJANGO_TIME_ZONE=Asia/Kolkata
```

Then run:

```bash
cd backend
source .venv/bin/activate
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

Important: `seed_demo` replaces the demo store's products, suppliers,
categories, sales, and stock logs. Do not run it on a database containing real
store data.

## Docker Run

Use this when Docker is installed and running.

```bash
docker compose up --build
```

Seed demo data:

```bash
docker compose exec backend python manage.py seed_demo
```

Open:

- Frontend: `http://localhost:5173`
- Backend docs: `http://localhost:8000/api/docs/`

## Useful Commands

Backend checks:

```bash
cd backend
source .venv/bin/activate
python manage.py check
python manage.py migrate
python manage.py seed_demo
```

Inspect migration and database state:

```bash
python manage.py showmigrations
python manage.py shell -c "from django.db import connection; print(connection.vendor, connection.settings_dict['NAME'])"
mysql -h 127.0.0.1 -u storepulse -p -e "SELECT table_name FROM information_schema.tables WHERE table_schema='storepulse';"
```

Frontend checks:

```bash
cd frontend
npm run build
```

Stop local ports if needed:

```bash
lsof -ti:8000 | xargs kill
lsof -ti:5173 | xargs kill
```

## Common Errors

### `ModuleNotFoundError: No module named rest_framework`

Backend dependencies are not installed in the active environment.

Fix:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

### `npm: command not found`

Node.js/npm is not installed or not added to PATH.

Fix: install Node.js from `https://nodejs.org/`, then reopen the terminal.

### `listen EPERM`

Your environment blocked port binding. Try a different terminal, run as a normal local command, or use Gunicorn for backend:

```bash
cd backend
source .venv/bin/activate
gunicorn storepulse.wsgi:application --bind 127.0.0.1:8000 --workers 1
```

### Frontend Cannot Connect To Backend

Check:

- Backend is running on `http://127.0.0.1:8000`
- Frontend `.env` has `VITE_API_URL=http://127.0.0.1:8000/api`
- `CORS_ALLOWED_ORIGINS` includes `http://127.0.0.1:5173`

### `Access denied for user 'storepulse'`

The MySQL host identity or password does not match. Re-run the `CREATE USER`,
`ALTER USER`, `GRANT`, and `FLUSH PRIVILEGES` statements from the recommended
MySQL setup. Create both `localhost` and `127.0.0.1` users.

### `Unknown database 'storepulse'`

Create the database from a root MySQL session:

```sql
CREATE DATABASE storepulse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Port 8000 or 5173 Is Already In Use

Check the process:

```bash
lsof -nP -iTCP:8000 -sTCP:LISTEN
lsof -nP -iTCP:5173 -sTCP:LISTEN
```

Stop the old development server with `Ctrl+C`, or run the new server on a
different port.

### Reset Only the Demo Database

This deletes all data in `storepulse`:

```bash
mysql -u root -p -e "DROP DATABASE storepulse; CREATE DATABASE storepulse CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
cd backend
source .venv/bin/activate
python manage.py migrate
python manage.py seed_demo
```
