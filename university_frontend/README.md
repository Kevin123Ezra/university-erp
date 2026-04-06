# University Frontend

React portal for the University ERP.

## What it does

- Authenticates against Odoo sessions
- Shows student, faculty, and admin workspaces
- Talks to Odoo through `/web` and `/uni` JSON-RPC endpoints
- Runs on Vite during development

## Requirements

- Node.js installed
- Odoo backend running on `http://localhost:8069`
- `University Base` installed and upgraded

## Install

Use `npm.cmd` in PowerShell on this machine:

```powershell
npm.cmd install
```

## Run

```powershell
npm.cmd run dev
```

Open:

- `http://localhost:5173`

## VS Code Shortcut

If you open the repository root in VS Code, press `Ctrl+Shift+B`.

That uses the workspace task runner to start:

- Odoo backend
- React frontend

## Main Files

- `src/App.jsx`
- `src/styles.css`
- `vite.config.js`

## Dev Notes

- The frontend proxies API requests to the Odoo backend.
- Browser hard refresh is often needed after UI changes.
- If backend payloads change, restart Odoo and upgrade `uni_base`.
