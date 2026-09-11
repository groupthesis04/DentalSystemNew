# Database Beginner Guide

This folder contains the MySQL structure used by the dental system.

## Files

- `schema.sql` creates the database tables, indexes, and relationships.
- `data/` contains legacy JSON data used only for migration or isolated testing, when present.

The Python backend uses the tables automatically through `backend/mysql_store.py`. Normal patient,
appointment, and treatment changes should be made through the application, not by manually editing
database rows.

## Initial Setup

Open `schema.sql` in HeidiSQL, select your MySQL server, and run the script once. Then configure the
connection values in `backend/.env`.

After setup, start the complete system from the project folder:

```powershell
python backend/server.py --host 127.0.0.1 --port 8000
```

The backend connects to MySQL and serves the built Vue frontend at `http://127.0.0.1:8000`.
