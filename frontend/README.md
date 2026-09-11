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
| Calls to the Python backend          | `src/services/api.js`                          |
| Form validation                      | `src/services/validation.js`                   |
| Dates, money, and display helpers    | `src/services/format.js`                       |
| Main website styles                  | `styles.css`                                   |
| Dashboard and dark-theme styles      | `src/dashboard-theme.css`                      |

## Simple Application Flow

1. `index.html` creates the empty `<div id="app">` browser container.
2. `src/main.js` starts Vue inside that container.
3. `src/App.vue` chooses the public, admin, or patient view from the URL.
4. A view uses small components for repeated interface elements.
5. `src/services/api.js` sends requests to the Python backend.

The files in `src/components/` are necessary shared pieces. For example, both dashboards use
`PortalHeader.vue`, `PortalSidebar.vue`, and `NotificationMenu.vue`. Keeping each piece separate
prevents the same code from being copied into several pages.

## Commands

From the `frontend` folder:

```powershell
npm.cmd install
npm.cmd run dev
```

`install` is needed only the first time. `dev` starts the Vue frontend at
`http://127.0.0.1:5173` and refreshes the browser whenever you save a Vue file.

```powershell
npm.cmd run format
```

`format` is optional and makes the Vue source consistent and readable. The Python backend runs
separately on port `8000` and Vite forwards `/api` requests to it automatically.
