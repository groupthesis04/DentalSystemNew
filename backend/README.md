# BORJA Dental Django Backend

The backend now uses Django, Django ORM, Django sessions, CSRF protection, and the
existing MySQL `dental_clinic` database. The Vue/Vite frontend remains separate.

## First-time setup

Start MySQL and create an empty `dental_clinic` database. From the project root in
PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
Copy-Item backend\.env.example backend\.env
python backend\manage.py migrate
python backend\manage.py createsuperuser
```

Edit `backend/.env` before migrating. Use `python backend\manage.py import_legacy_data`
only when upgrading an older installation with populated legacy tables. The import is
idempotent and does not create duplicate rows when repeated.

## Start the backend

```powershell
.\.venv\Scripts\python.exe backend\manage.py runserver 0.0.0.0:8000
```

For local desktop use, open the frontend at `http://127.0.0.1:5173`. To test from a
phone on the same Wi-Fi, start Vite with its configured `0.0.0.0` host and open the
computer's LAN address, for example `http://192.168.1.10:5173`.

## Run tests

The database account does not need permission to create a MySQL test database. Tests
therefore use a disposable in-memory SQLite database:

```powershell
$env:DRMS_TEST_SQLITE="1"
python backend\manage.py test tests.test_django_api
Remove-Item Env:DRMS_TEST_SQLITE
```

Normal application commands still use MySQL.

See `DJANGO_BACKEND_GUIDE.md` in the project root for the complete beginner guide.
