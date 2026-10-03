# StrangerChat

A starter social-chat application with a FastAPI/SQLite backend and a static
HTML/CSS/JavaScript frontend. Features include registration and login, JWT
authentication, user discovery, 1-to-1 conversations, persistent and real-time
messages, typing indicators, online status, read receipts, blocking, and reports.

## Run the backend on Windows

Open PowerShell and run:

```powershell
Set-Location "E:\code\full stack\backend"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe seed.py
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Uvicorn requires the `module:application` form (`main:app`); `main` alone is not
a valid application target. The database is stored beside the backend source,
regardless of the terminal's working directory.

Open the API documentation at <http://127.0.0.1:8000/docs>.

Demo accounts (each password is `password123`):

- alice@example.com
- bob@example.com
- charlie@example.com

## Run the frontend

Open `frontend/index.html` using VS Code Live Preview. The frontend calls
`http://127.0.0.1:8000` by default. Localhost and 127.0.0.1 Live Preview origins
are allowed by the backend.

For a different frontend origin (for example, a forwarded Codespaces URL), set
`STRANGERCHAT_CORS_ORIGINS` to a comma-separated list of exact origins before
starting the backend. Set `STRANGERCHAT_SECRET_KEY` to a private random value
outside local development. The optional `DATABASE_URL` setting can point to a
different SQLAlchemy database URL when its driver is installed.

To override the API URL for the browser, run this in its developer console and
reload:

```js
localStorage.setItem("apiBase", "https://YOUR-API-ORIGIN")
```

## Deployment

This is a development build. Before public deployment, configure a strong
`STRANGERCHAT_SECRET_KEY`, restrict allowed CORS origins, use HTTPS, add rate
limiting and moderation controls, and review the database and abuse-prevention
requirements for the deployment environment.
