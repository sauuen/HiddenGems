# Hidden Gems

## Structure

- `frontend/` — Kivy app. It contains the UI, local favorites, local location selection, and calls the backend through HTTP.

The frontend only has `BACKEND_URL`. The OpenAI and Google Places keys is hidden and only ran through render

## Backend setup

Backend is ran on Render, no need to think about it. Added the files to here so backend can be seen

## Frontend setup

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
