# CertMind local development without Docker

Docker is optional. CertMind can run directly on Windows with Python and Node.js.

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and set GOOGLE_API_KEY and a strong JWT_SECRET
uvicorn main:app --reload --port 8000
```

Health checks:
- http://localhost:8000/health
- http://localhost:8000/ready

## Frontend

In a second PowerShell window:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 in Chrome.

Required values are JWT_SECRET, GOOGLE_API_KEY, FRONTEND_URL, and DB_PATH. Keep the existing SQLite database and Chroma data path when upgrading. Back up the database, uploaded files, and vector data before migrations.

## Safe verification checklist

1. Confirm /health returns status: ok.
2. Confirm /ready returns status: ready.
3. Register and log in.
4. Upload one Markdown file from Personal Knowledge.
5. Wait for ready status.
6. Run one evaluation and one small experiment.
7. Check Observability after a model call.
