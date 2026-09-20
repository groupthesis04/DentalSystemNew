# Frontend Beginner Guide

The frontend is a Vue 3 application. Make frontend changes only in `src/` and the two CSS files
listed below. Vite reads those source files directly while you work.

## Where to Make Changes

| What you want to change              | File or folder                                 |
| ------------------------------------ | ---------------------------------------------- |
| Public website                       | `src/views/PublicHome.vue`                     |
| Admin dashboard shell                | `src/views/DoctorDashboard.vue`                |
| Patient dashboard                    | `src/views/PatientDashboard.vue`               |
| Patient management                   | `src/components/doctor/PatientManagement.vue`  |
| Appointments and clinic availability | `src/components/doctor/ScheduleManagement.vue` |
| Services, promos, and feedback       | `src/components/doctor/ContentManagement.vue`  |
| Shared header, sidebar, modal, icons | `src/components/`                              |
| Calls to the Django backend          | `src/services/api.js`                          |
| Form validation                      | `src/services/validation.js`                   |
| Dates, money, and display helpers    | `src/services/format.js`                       |
| Main website styles                  | `styles.css`                                   |
| Dashboard and dark-theme styles      | `src/dashboard-theme.css`                      |

## Simple Application Flow

1. `index.html` creates the empty `<div id="app">` browser container.
2. `src/main.js` starts Vue inside that container.
3. `src/App.vue` chooses the public, admin, or patient view from the URL.
4. A view uses small components for repeated interface elements.
5. `src/services/api.js` sends JSON requests to the Django backend.

The files in `src/components/` are necessary shared pieces. For example, both dashboards use
`PortalHeader.vue`, `PortalSidebar.vue`, and `NotificationMenu.vue`. Keeping each piece separate
prevents the same code from being copied into several pages.

## First-Time Setup

From the `frontend` folder:

```powershell
npm.cmd install
```

## Start the Frontend

Start Django from the project root first. Then, from the `frontend` folder:

```powershell
npm.cmd run dev
```

`install` is needed only the first time. `dev` starts the Vue frontend and refreshes the browser
whenever you save a Vue file. On this computer, open `http://127.0.0.1:5173`.

## Open on a Phone

1. Connect the computer and phone to the same Wi-Fi network.
2. Start the Django backend from the main project folder:

```powershell
.\.venv\Scripts\python.exe backend\manage.py runserver 0.0.0.0:8000
```

3. In a second terminal, start Vue from the `frontend` folder:

```powershell
npm.cmd run dev
```

4. Find the computer's Wi-Fi IPv4 address by running `ipconfig` and looking under the active
   Wireless LAN adapter.
5. On the phone, open `http://COMPUTER-IP:5173`. For example, if the address is
   `192.168.68.115`, open `http://192.168.68.115:5173`.

If Windows asks whether Node.js may communicate through the firewall, allow it on **Private
networks**. The phone uses only port `5173`; Vite forwards API requests to the backend on port
`8000` automatically.

## Optional Local Test Accounts

Copy `.env.example` to `.env.development.local` and enter development-only test credentials to
show account shortcuts in the login modal. Restart Vite after changing the file. The local file
is ignored and must never be committed or included in a submission package. Keep password values
in double quotes when they contain `#`, because unquoted `#` begins an environment-file comment.

## Formatting

```powershell
npm.cmd run format
```

`format` is optional and makes the Vue source consistent and readable. The Django backend runs
separately on port `8000` and Vite forwards `/api` requests to it automatically.
