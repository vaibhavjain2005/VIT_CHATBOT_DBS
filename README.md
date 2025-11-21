# VIT Admission Chatbot (VIT_CHATBOT_DBS)

Lightweight README for local development, setup and deployment-ready repository.

## Overview
A chatbot for VIT admissions that supports:
- Intent classification (cutoff, rank_prediction, faq)
- Rank prediction and cutoff lookup
- Backend: FastAPI, MongoDB, embedding utilities, LLM adapters
- Frontend: React app located in `admission-chatbot/`
- Database seeding scripts in `scripts/`

## Repository layout
- services/          — backend adapters (groq_service.py, mongodb_service.py, ...)
- utils/             — embedding utilities
- scripts/           — `seed.py`, `seed_database.py`
- admission-chatbot/ — React frontend
- requirements.txt   — Python dependencies
- .env               — local environment variables (not checked in)

## Prerequisites
- Python 3.11 (recommended)
- Node.js + npm
- MongoDB (local or Atlas)
- Optional: Visual C++ Build Tools (if pip compiles packages on Windows)

## Quick setup (Windows — PowerShell)
1. Ensure Python 3.11 is available:
   py -3.11 --version

2. Create and activate virtual environment:
```powershell
py -3.11 -m venv venv
.\venv\Scripts\activate
```

3. Upgrade packaging tools:
```powershell
python -m pip install --upgrade pip setuptools wheel
```

4. Install binary numeric packages first to avoid builds:
```powershell
python -m pip install --prefer-binary numpy scipy
python -m pip install --prefer-binary -r requirements.txt
```

If pip tries to compile scikit-learn and errors with:
`Microsoft Visual C++ 14.0 or greater is required.`  
Either install Visual C++ Build Tools (Desktop development with C++) or use conda:

Conda approach:
```powershell
conda create -n vitbot python=3.11
conda activate vitbot
conda install -c conda-forge scikit-learn numpy scipy
pip install -r requirements.txt --no-deps
```

## Environment variables
Create a `.env` in project root with required keys:
```
MONGODB_URL=mongodb://localhost:27017/
EMBEDDING_MODEL_NAME=all-mpnet-base-v2
GROQ_API_KEY=...
GOOGLE_API_KEY=...
```

## Run backend
Start MongoDB, then:
```powershell
# with venv activated
python -m uvicorn main:app --reload
# adjust entrypoint if different
```
API docs available at http://127.0.0.1:8000/docs

## Seed database
```powershell
python scripts/seed.py
# or
python scripts/seed_database.py
```

## Frontend
```powershell
cd admission-chatbot
npm install
npm start
# or npm run dev if using Vite
```
Configure frontend API base URL in `admission-chatbot/.env` or the app's environment file.

## Frontend compatibility notes
- The frontend expects `rank_prediction` JSON; if backend format changes update parsing in components under `admission-chatbot/src/components/`.
- Example tolerant parser is recommended to handle minor schema changes.

## Troubleshooting
- Wrong Python version in VS Code: Command Palette → Python: Select Interpreter or add `.vscode/settings.json` with:
```json
{
  "python.defaultInterpreterPath": "C:\\Path\\To\\Python311\\python.exe"
}
```
- Virtual env not activating: run PowerShell as Administrator and set:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
- scikit-learn build errors: install Visual C++ Build Tools or use conda as above.

## Testing & linting
- Add tests under `tests/` and run with pytest
- Use black/flake8 for formatting and linting

## Deployment
- Containerize with Docker (create Dockerfile for backend + frontend)
- Use a managed MongoDB (Atlas) for production
- Configure secrets as environment variables in deployment environment

## License
Add LICENSE file to specify project license.
