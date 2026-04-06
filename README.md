# University ERP

This repository contains the custom code for the project:

- the Odoo addon in [`university/uni_base`](./university/uni_base)
- the React portal in [`university_frontend`](./university_frontend)

It is not a full Odoo source-code mirror. The React app depends on a running Odoo server and uses Odoo for authentication, data, and business logic.

## What is in this repo

- `university/uni_base`
  Custom Odoo module with models, views, controllers, seed data, and AI integration
- `university_frontend`
  React + Vite portal for students, faculty, librarian, and admin flows
- `.vscode`
  Workspace tasks and launch configuration
- `odoo.conf.example`
  Example local Odoo config
- `.env`
  Gemini API key placeholder file

## Main features

### Student portal

- login through Odoo session auth
- dashboard with pending assignments, pending fees, upcoming exams, and enrolled classes
- class detail view from the home page
- weekly timetable
- course registration
- assignment submission
- online exams
- results and resit requests
- fees page with pending and paid sections
- library page
- study assistant with notes or PDF upload
- notification drawer and browser notifications

### Faculty portal

- teaching overview
- faculty timetable
- students grouped by assigned course
- at-risk filter for students
- assignment creation, editing, publishing, deleting
- submission review and grading
- AI feedback drafting while grading
- exam creation, editing, publishing, deleting
- written/upload answer review and grading

### Librarian and admin

- admin can create students, faculty, and courses
- admin can assign courses to faculty
- librarian/admin can process library returns
- fines can be added to student fees
- admin can run at-risk scans

### AI features

- at-risk student prediction
- study assistant
- feedback drafting for faculty

## Demo users

Seed data currently creates these usernames:

- `student`
- `student2`
- `faculty`
- `faculty1`
- `uniadmin`

Passwords are seeded in the database, not documented in the frontend. Reset them from Odoo if needed.

## What you need locally

- PostgreSQL
- Odoo runtime and dependencies
- Node.js
- the Odoo Python environment

## Odoo setup

1. Install or keep a local Odoo instance.
2. Copy [`odoo.conf.example`](./odoo.conf.example) to `odoo.conf`.
3. Make sure `addons_path` includes this repo's `university` directory.
4. Set the database connection for your machine.

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

## Gemini API key

This repo includes:

- [`.env`](./.env)
- [`.env.example`](./.env.example)

Both are intentionally empty in GitHub. Put your Gemini key in `.env` locally:

```env
UNI_GEMINI_API_KEY=your_real_key_here
```

Do not commit a real API key.

## Running the project

You need both servers running:

1. the Odoo server on port `8069`
2. the React dev server from `university_frontend`

The React app on its own is not enough. It calls the Odoo backend for login, data, grading, AI actions, and everything else.

### VS Code

Use `Ctrl+Shift+B`.

Available tasks:

- `Start Odoo`
- `Upgrade University Base`
- `Start Frontend`
- `Start All`

Typical flow:

1. run `Upgrade University Base` after backend changes
2. run `Start Odoo`
3. run `Start Frontend`

### Manual commands

From the repo root:

Start Odoo:

```powershell
.\..\python\python.exe .\odoo-bin --config=.\odoo.conf -d admin
```

Upgrade the addon:

```powershell
.\..\python\python.exe .\odoo-bin --config=.\odoo.conf -d admin -u uni_base --stop-after-init
```

Start the React app:

```powershell
cd .\university_frontend
npm.cmd install
npm.cmd run dev
```

Then open:

- Odoo: `http://localhost:8069`
- React portal: `http://localhost:5173`

## Development notes

- backend changes in `university/uni_base` usually require an addon upgrade
- frontend-only changes in `university_frontend` usually just need a browser refresh
- the React app uses the Odoo session and API routes under `/web` and `/uni`

## Important files

- [`university/uni_base/controllers/api.py`](./university/uni_base/controllers/api.py)
- [`university/uni_base/models/res_users.py`](./university/uni_base/models/res_users.py)
- [`university/uni_base/models/university_core.py`](./university/uni_base/models/university_core.py)
- [`university/uni_base/models/university_extended.py`](./university/uni_base/models/university_extended.py)
- [`university/uni_base/models/university_ai.py`](./university/uni_base/models/university_ai.py)
- [`university_frontend/src/App.jsx`](./university_frontend/src/App.jsx)
- [`university_frontend/src/styles.css`](./university_frontend/src/styles.css)

## What to push to GitHub

Push the project code:

- `university/`
- `university_frontend/`
- `.vscode/`
- `README.md`
- `.gitignore`
- `.env`
- `.env.example`
- `odoo.conf.example`

Do not push machine-specific runtime files like:

- local `odoo.conf` with real credentials
- filled-in secrets
- logs
- `node_modules`
- database or filestore data
- the full Odoo source tree unless you intentionally want to maintain an Odoo fork
