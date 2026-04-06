# University ERP

Custom university ERP built on top of Odoo, with a separate React portal frontend.

This repository is intended to store the custom university project code, not the full Odoo source tree. In a production or team setup, install Odoo separately and load the addon in `university/uni_base` through `addons_path`.

## What Is In This Repo

- `university/uni_base`
  Custom Odoo addon for the university ERP
- `university_frontend`
  React + Vite frontend portal
- `.vscode/tasks.json`
  VS Code tasks for starting Odoo and the frontend
- `.vscode/launch.json`
  VS Code debug configuration for Odoo
- `odoo.conf.example`
  Example Odoo config to adapt locally

## Main Features

### Branding and entry

- Branded university login experience
- React login against Odoo session authentication
- Visionary Minds University branding
- Student notification drawer with browser notifications

### Student portal

- Overview with pending assignments, fees, exams, and enrolled classes
- Expandable course cards on the home page
- Weekly timetable view
- Course registration from the courses page
- Assignment submission from the assignments page
- Quiz and upload assignment flows
- Exam taking for MCQ, text-answer, and upload-answer questions
- Results and resit requests
- Pending vs paid fee sections
- Combined library view

### Faculty portal

- Faculty overview and teaching timetable
- Students grouped by assigned courses
- Assignment create/edit/publish/delete
- Submission review and grading
- Exam create/edit/publish/delete
- Manual grading for non-MCQ exam answers

### Admin portal

- Create students, faculty, and courses
- Assign courses to faculty
- View course registrations
- System-wide visibility across students, academics, exams, issues, and finance

### Backend domain models

- Students, faculty, departments, terms, courses
- Registrations, timetable, attendance, grades, GPA
- Assignments and submissions
- Exams, questions, answers, results, resits
- Fees, scholarships, notifications, issues, library records

## Demo Accounts

- `student / student123`
- `faculty / faculty123`
- `faculty1 / faculty123`
- `uniadmin / uniadmin123`

## Recommended Repo Contents For GitHub

Push these project folders/files:

- `university/`
- `university_frontend/`
- `.vscode/`
- `README.md`
- `.gitignore`
- `odoo.conf.example`

Do not push:

- your local `odoo.conf`
- `node_modules`
- logs
- local database/filestore data
- machine-specific secrets
- the full Odoo source tree unless you intentionally want to maintain an Odoo fork

## Prerequisites

- Python installed and selected in VS Code
- PostgreSQL running
- Odoo installed separately
- Node.js installed

## Odoo Setup

1. Install Odoo separately.
2. Copy `odoo.conf.example` to `odoo.conf`.
3. Update `addons_path` so it includes:
   - your Odoo core addons path
   - this repo's `university` folder
4. Set your database connection values.

Example:

```ini
[options]
addons_path = C:\path\to\odoo\addons,C:\path\to\repo\university
db_host = localhost
db_port = 5432
db_user = openpg
db_password = openpgpwd
http_port = 8069
```

## Frontend Setup

From `university_frontend`:

```powershell
npm.cmd install
```

## VS Code Setup

Set the workspace Python interpreter first.

The VS Code tasks and debugger use:

- `python.defaultInterpreterPath`

So any developer can use this setup by selecting their own Python interpreter in VS Code.

## Start Development

### Option 1: VS Code tasks

Press `Ctrl+Shift+B`.

That starts:

- Odoo backend
- React frontend

Available tasks:

- `Start Odoo`
- `Upgrade University Base`
- `Start Frontend`
- `Start All`

### Option 2: Manual commands

Backend:

```powershell
python .\odoo-bin -c .\odoo.conf -d admin
```

Upgrade addon after backend changes:

```powershell
python .\odoo-bin -c .\odoo.conf -d admin -u uni_base --stop-after-init
```

Frontend:

```powershell
cd university_frontend
npm.cmd run dev
```

## Daily Workflow

1. Start the backend and frontend.
2. Upgrade `uni_base` after Python/XML model/view/controller changes.
3. Hard refresh the browser after major frontend changes.
4. Restart Odoo when backend code changes are not picked up by the running process.

## Important Files

- `university/uni_base/__manifest__.py`
- `university/uni_base/controllers/api.py`
- `university/uni_base/models/res_company.py`
- `university/uni_base/models/res_users.py`
- `university/uni_base/models/university_core.py`
- `university/uni_base/models/university_extended.py`
- `university_frontend/src/App.jsx`
- `university_frontend/src/styles.css`

## Notes

- The React frontend proxies `/web` and `/uni` to Odoo during development.
- The frontend depends on the Odoo session login flow.
- This repo is best treated as custom project code layered on top of a separate Odoo install.
