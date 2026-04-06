# University ERP

Custom university ERP built as:

- an Odoo addon in [`university/uni_base`](./university/uni_base)
- a separate React portal in [`university_frontend`](./university_frontend)

This repo stores the project code only. It is not meant to include the full Odoo source tree in GitHub.

## Repo Layout

- `university/uni_base`
  Main Odoo addon: models, views, controllers, seed data, AI services
- `university_frontend`
  React + Vite portal for students, faculty, librarians, and admins
- `.vscode`
  VS Code tasks, launch config, workspace Python interpreter
- `odoo.conf.example`
  Example local Odoo config
- `.env.example`
  Example local AI config

## Implemented Features

### Branding and access

- Visionary Minds University branding in Odoo and React
- custom login experience
- React login using Odoo session authentication
- role-aware navigation and dashboards

### Student features

- overview with pending assignments, pending fees, upcoming exams, and enrolled classes
- weekly timetable
- course registration from the courses page
- assignment submission from the assignments page
- quiz assignments and upload assignments
- online exams with MCQ, text, and upload question types
- results and resit requests
- pending vs paid fees view
- combined library page
- study assistant with note input or PDF upload
- browser notifications drawer

### Faculty features

- faculty overview and teaching timetable
- students grouped by assigned courses
- at-risk student filtering
- assignment create, edit, publish, delete
- submission review and grading
- AI feedback draft generation during grading
- exam create, edit, publish, delete
- manual grading for written and upload exam answers

### Librarian features

- `faculty1` seeded as librarian
- librarian and admin can process library returns
- fine amount can be applied on return
- fine creates a fee invoice for the student
- student notification is created for a library fine

### Admin features

- create students, faculty, and courses
- assign courses to faculty
- run at-risk scan manually
- view registrations, issues, fees, library records, exams, and academic data

### AI features

- at-risk student predictor
  - risk snapshots stored in Odoo
  - weekly cron plus manual admin trigger
  - advisor notification/activity for high and critical students
- study assistant
  - summary
  - practice MCQs
  - gap analysis
- AI feedback writer
  - faculty can draft constructive feedback from mark + note

### Core backend models

- departments
- terms
- faculty
- students
- courses
- timetable
- attendance
- grades and GPA
- assignments and submissions
- exams, questions, answers, results, resits
- fees and scholarships
- notifications
- issues
- library items and loans
- student risk snapshots

## Demo Accounts

Seeded demo users:

- `student`
- `student2`
- `faculty`
- `faculty1`
- `uniadmin`

Passwords are seeded in the database by demo data and can be reset from Odoo user management if needed.

## Local Prerequisites

- PostgreSQL
- Odoo runtime and dependencies
- Node.js
- the bundled Odoo Python or another Python environment with all Odoo dependencies installed

## Odoo Setup

1. Install or keep Odoo locally.
2. Copy `odoo.conf.example` to `odoo.conf`.
3. Make sure `addons_path` includes this repo’s `university` directory.
4. Set database connection values for your local machine.

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

## AI Setup

Use a local `.env` file in the repo root.

1. Copy `.env.example` to `.env`
2. Set:

```env
UNI_GEMINI_API_KEY=your_real_key_here
```

Resolution order used by the addon:

1. real environment variable `UNI_GEMINI_API_KEY`
2. repo-root `.env`
3. company setting fallback

`.env` is ignored by git.

## VS Code Setup

The workspace defaults to:

- [`..\\python\\python.exe`](../python/python.exe)

That is the bundled Odoo Python used by the tasks and debugger. If your setup differs, update:

- [`.vscode/settings.json`](./.vscode/settings.json)

Do not use the Windows Store Python for Odoo unless it has all required Odoo packages installed.

## Start Development

### VS Code

Press `Ctrl+Shift+B`.

Available tasks:

- `Start Odoo`
- `Upgrade University Base`
- `Start Frontend`
- `Start All`

Recommended workflow:

1. run `Upgrade University Base` after backend changes
2. run `Start Odoo`
3. run `Start Frontend`

### Manual Commands

From the repo root:

Start Odoo:

```powershell
.\..\python\python.exe .\odoo-bin --config=.\odoo.conf -d admin
```

Upgrade the addon after backend changes:

```powershell
.\..\python\python.exe .\odoo-bin --config=.\odoo.conf -d admin -u uni_base --stop-after-init
```

Start the frontend:

```powershell
cd .\university_frontend
npm.cmd install
npm.cmd run dev
```

## Daily Workflow

1. edit backend code in `university/uni_base`
2. run the `uni_base` upgrade
3. restart Odoo if needed
4. edit frontend code in `university_frontend`
5. hard refresh the browser when checking UI changes

## Important Files

- [`university/uni_base/__manifest__.py`](./university/uni_base/__manifest__.py)
- [`university/uni_base/controllers/api.py`](./university/uni_base/controllers/api.py)
- [`university/uni_base/models/res_company.py`](./university/uni_base/models/res_company.py)
- [`university/uni_base/models/res_users.py`](./university/uni_base/models/res_users.py)
- [`university/uni_base/models/university_core.py`](./university/uni_base/models/university_core.py)
- [`university/uni_base/models/university_extended.py`](./university/uni_base/models/university_extended.py)
- [`university/uni_base/models/university_ai.py`](./university/uni_base/models/university_ai.py)
- [`university_frontend/src/App.jsx`](./university_frontend/src/App.jsx)
- [`university_frontend/src/styles.css`](./university_frontend/src/styles.css)

## GitHub Contents

For the project repo, push the custom project files only:

- `university/`
- `university_frontend/`
- `.vscode/`
- `README.md`
- `.gitignore`
- `.env.example`
- `odoo.conf.example`

Do not push local runtime/config artifacts like:

- local `odoo.conf`
- `.env`
- logs
- `node_modules`
- database storage
- the full Odoo source tree unless you intentionally want an Odoo fork

## Notes

- The React frontend talks to Odoo through `/web` and `/uni` routes.
- The frontend depends on an Odoo session.
- Some Odoo 19 warnings still remain in local logs:
  - PostgreSQL 12 below recommended minimum
  - legacy `_sql_constraints`
  - manifest `author` missing
  - login template XPath class warnings

Those warnings do not currently block startup or the main flows.
