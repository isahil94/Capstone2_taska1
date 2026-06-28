# Onboarding — Capstone 2 Code Intelligence

This document explains how to run the backend and frontend, clone a repository, and view interactive architecture graphs.

Requirements
- Python 3.11+, Git, Node 18+ (for frontend)

Backend
- From the `backend` folder:

```powershell
cd "f:\Projects\Capstone 2\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend
- From the `frontend` folder:

```powershell
cd "f:\Projects\Capstone 2\frontend"
npm install
npm run dev
```

Usage
- Open the frontend in your browser.
- Use "GitHub repo URL" to enter a repository URL (e.g. `https://github.com/owner/repo.git`).
- Click "Clone & Build Graphs" to start an asynchronous job that clones the repo and builds graph snapshots.
- When job completes, the interactive graph will appear. Click nodes to run change-impact analysis and highlight affected nodes.

Notes
- The backend persists graphs into the local DB. Large repositories may take time to clone and analyze.
- The clone/graph job reports status via the `GET /jobs/{job_id}` endpoint.
