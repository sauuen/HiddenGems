# Hidden Gems

This version separates the project into two parts so API keys are not shown in the frontend deliverable.

## Structure

- `frontend/` — Kivy app. It contains the UI, local favorites, local location selection, and calls the backend through HTTP.
- `backend/` — FastAPI server. It contains Google Places and OpenAI logic, and reads API keys from a local `.env` file.

## Why this is safer

The frontend only has `BACKEND_URL`. The OpenAI and Google Places keys stay inside `backend/.env`, which is ignored by Git.

## Backend setup

Backend is ran on Render, no need to think about it

## Frontend setup

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

If the backend runs somewhere else, copy `frontend/.env.example` to `frontend/.env` and change `BACKEND_URL`.

## Important exam note

Do not submit real `.env` files. Submit `.env.example` only.

If a real key has already been uploaded or committed anywhere, rotate/delete that key in the provider dashboard and create a new one.
