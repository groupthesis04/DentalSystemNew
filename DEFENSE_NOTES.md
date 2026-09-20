# BORJA Dental Thesis Defense Notes

This file contains private study material. It is separate from the official setup and
technical documentation and is not required to run the system.

## Code to Review

1. `backend/dental_backend/settings.py`: MySQL, apps, middleware, sessions, and CSRF.
2. `backend/dental_backend/urls.py`: root API routing.
3. `backend/accounts/models.py`: custom email user and patient profile.
4. `backend/accounts/views.py`: login, registration, profile, and role checks.
5. `backend/scheduling/models.py`: appointment and availability relationships.
6. `backend/scheduling/views.py`: booking validation and slot transactions.
7. `backend/records/views.py`: treatment completion and payment calculation.
8. `frontend/src/services/api.js`: Fetch, cookies, JSON, and CSRF headers.
9. `frontend/vite.config.js`: `/api` development proxy.

## Possible Panel Questions and Answers

### What frontend framework does the system use?

Vue.js 3, with Vite as the development server and production build tool.

### What backend framework does the system use?

Django 5.2.

### Why use Django?

Django provides an ORM, authentication, sessions, CSRF protection, migrations, URL
routing, validation tools, and an admin site in one maintained framework.

### What backend was used before Django?

The earlier version used Python `ThreadingHTTPServer`, `BaseHTTPRequestHandler`, custom
routes and sessions, and `mysql-connector-python`.

### Why is ThreadingHTTPServer not a complete web framework?

It receives HTTP requests but does not provide models, an ORM, migrations,
authentication, CSRF middleware, permissions, forms, or a standard application
structure.

### What is Django ORM and why is it used?

The ORM maps Python model classes and query methods to database tables and SQL. It makes
relationships and queries easier to read, supports migrations, reduces manual SQL, and
keeps data access consistent.

### What database does the system use?

MySQL. The database is named `dental_clinic` in local development.

### How does Vue communicate with Django?

Vue uses the browser Fetch API to call JSON endpoints under `/api`. Vite proxies those
requests to Django during development.

### What is CSRF protection?

Cross-Site Request Forgery protection prevents another site from making unwanted write
requests through a logged-in browser. Django verifies a token on state-changing requests.

### How are passwords and sessions protected?

Django stores salted password hashes rather than plain-text passwords. Successful login
creates a database-backed session identified by an HttpOnly cookie.

### How are patient and doctor roles separated?

`User.role` stores `patient` or `doctor`. Private API views verify authentication and the
required role before reading or changing data.

### How is patient data ownership enforced?

Patient appointment and treatment queries are filtered through the `PatientProfile`
linked to `request.user`. A browser-provided patient ID cannot override that ownership
filter.

### What happens when an appointment is completed?

The doctor must submit a treatment record. Django saves the record and marks the linked
appointment completed in the same database transaction.

### How does the notification system work?

Appointment and treatment actions create notifications for affected accounts. The API
returns only notifications belonging to the authenticated user.

### Why keep Vue instead of using Django templates?

The existing Vue interface provides the complete interactive design. Django acts as a
JSON backend, allowing the frontend to remain intact.

### What happens after a guest clicks Book Appointment?

Vue retains the draft while the patient logs in or registers. On confirmation, Django
revalidates the authenticated patient, service, dentist, date, time, availability,
conflicts, and booking token before inserting the appointment and creating notifications.
