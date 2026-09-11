# Dental Record Management System

This project uses a Python HTTP backend, a Vue 3/Vite frontend, and MySQL persistence.

## Project layout

- `frontend/` - Vue components, Vite configuration, styles, and browser assets
- `backend/` - HTTP server, routes, MySQL adapter, tests, tools, and configuration
- `database/` - MySQL schema and legacy JSON migration data

## Beginner Code Map

You normally only need to open the route file for the feature you are changing:

| Feature | File |
| --- | --- |
| Login and registration | `routes/auth.py` |
| Patients | `routes/patients.py` |
| Treatments | `routes/treatments.py` |
| Appointments | `routes/appointments.py` |
| Clinic availability | `routes/availability.py` |
| Services, promos, and feedback | `routes/services.py` |
| Messages | `routes/messages.py` |
| Notifications | `routes/notifications.py` |

The remaining backend files support those features:

- `server.py` starts the web server and sends each API request to the correct route.
- `core.py` contains shared validation, security, sessions, and data helpers.
- `mysql_store.py` is the only file that translates application data to and from MySQL.
- `notifications.py` contains the small shared notification helpers.
- `tests/` checks important workflows automatically.

A request follows one predictable path: Vue calls `/api/...`, `server.py` selects a route, the route
validates the request, and `mysql_store.py` saves or reads MySQL data. Do not remove validation, CSRF,
rate limiting, or password hashing just to shorten the code; those longer sections protect patient data.

## Requirements

- Python 3.11 or newer
- MySQL Server 8.x
- Python packages from `backend/requirements.txt`
- Node.js 20 or newer

```powershell
python -m pip install -r backend/requirements.txt
```

## MySQL setup

Run `database/schema.sql` from MySQL Workbench or the MySQL command line using an administrator account. Then create a restricted application account and grant it access to the clinic database.

```sql
CREATE USER 'dental_app'@'localhost' IDENTIFIED BY 'replace-with-a-strong-password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX
  ON dental_clinic.* TO 'dental_app'@'localhost';
FLUSH PRIVILEGES;
```

Copy `backend/.env.example` to `backend/.env`, then replace every placeholder secret. The server reads that file automatically.

```text
DRMS_STORAGE=mysql
DRMS_DB_HOST=127.0.0.1
DRMS_DB_PORT=3306
DRMS_DB_NAME=dental_clinic
DRMS_DB_USER=dental_app
DRMS_DB_PASSWORD=your-strong-database-password
```

`DRMS_DB_AUTO_INIT=1` creates missing tables when the database account has permission. Set it to `0` after running `database/schema.sql` if schema creation should be administrator-controlled.

## Existing data migration

To import the current JSON records into an empty MySQL database:

```powershell
python backend/tools/migrate_json_to_mysql.py --source database/data/app_data.json
```

The migration refuses to replace existing clinic data. Use `--force` only after making a database backup and intentionally choosing replacement.

## Run

Start the Python API from the project folder:

```powershell
python backend/server.py --host 127.0.0.1 --port 8000
```

Open a second terminal and start the Vue frontend:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

`npm.cmd install` is needed only the first time. Open `http://127.0.0.1:5173` while developing.
Saving a Vue file updates the browser automatically. Port `8000` is API-only and redirects browser
pages to the Vue development server.

The clinic uses its existing doctor account. Public sign-up creates patient accounts only, preventing
additional administrator accounts from being created through the website.

Doctor accounts manage clinic schedules from **Appointments > Clinic availability**. An admin can select multiple dates in one month, set the dentist's time-in and time-out, and generate 15-, 30-, or 60-minute appointment slots in one batch. Pending requests leave a slot open; accepting one request closes that exact dentist, date, and time to patients and cancels competing pending requests. Cancelling the accepted appointment makes the slot available again.

For isolated migration or automated tests only, JSON storage remains available explicitly:

```powershell
python backend/server.py --storage json --data-file database/data/test.json --port 8000
```

## Security controls

- Central server-side field allowlists, size limits, normalization, and validation
- Client-side native constraints and JavaScript verification
- PBKDF2 password hashing with per-password salts
- Session-bound CSRF tokens and strict same-site cookies
- Same-origin enforcement and restrictive browser security headers
- Endpoint-specific IP rate limiting with `429` and `Retry-After`
- Off-screen honeypots on all submitted forms
- Role checks for doctor-only and patient-only operations

Set `DRMS_COOKIE_SECURE=1` when the application is served over HTTPS. Keep `.env` out of source control and use a dedicated MySQL account rather than `root` in production.
