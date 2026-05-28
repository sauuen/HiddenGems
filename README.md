# Hidden Gems

Hidden Gems is a restaurant discovery app that helps users find less tourist-heavy food spots. Instead of only recommending the most popular restaurants, the app focuses on places with good ratings but fewer reviews, making it easier to discover local and lesser-known restaurants.

The project has been split into a **frontend** and **backend** structure so API keys are not exposed in the client application.

## Project Structure

```text
HiddenGems/
│
├── frontend/          # Kivy desktop/mobile frontend
│   ├── main.py
│   ├── config.py
│   ├── services/
│   ├── ui/
│   ├── logic/
│   ├── models/
│   └── requirements.txt
│
├── backend/           # FastAPI backend hosted on Render
│   ├── app.py
│   ├── config.py
│   ├── services/
│   ├── logic/
│   ├── models/
│   └── requirements.txt
│
├── backend_map/       # Backend structure/map documentation
├── README.md
└── .gitignore
```

## How It Works

The frontend does not contain API keys. It sends requests to the backend, and the backend handles all external API calls.

```text
Frontend / Kivy app
        ↓
FastAPI backend hosted on Render
        ↓
Google Places API + OpenAI API
```

This keeps the API keys hidden from the frontend and makes the project safer to upload to GitHub.

## Hosted Backend

The backend is hosted on Render.

Backend URL:

```text
https://YOUR-RENDER-BACKEND-URL.onrender.com
```

FastAPI documentation can be viewed at:

```text
https://YOUR-RENDER-BACKEND-URL.onrender.com/docs
```

If the Render backend has been inactive for a while, it may take some time to start because the free Render tier can put services to sleep.

## Environment Variables

The backend uses environment variables for API keys.

These are required on Render:

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_PLACES_API_KEY=your_google_places_api_key
```

These keys are added in Render under:

```text
Render Dashboard → Web Service → Environment
```

The real `.env` file is not included in the GitHub repository.

Safe example files are included:

```text
backend/.env.example
frontend/.env.example
```

## Running the Frontend Locally

Go into the frontend folder:

```powershell
cd frontend
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run the app:

```powershell
python main.py
```

## Frontend Backend URL

The frontend connects to the hosted Render backend. The backend URL is configured in:

```text
frontend/config.py
```

The app can also use a local `.env` file if needed:

```env
BACKEND_URL=https://YOUR-RENDER-BACKEND-URL.onrender.com
```

However, the `.env` file is not uploaded to GitHub. It is only used locally.

## Running the Backend Locally

The backend is already hosted on Render, so this is not required for normal use. To run it locally for development:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Create a local `.env` file inside the backend folder:

```env
OPENAI_API_KEY=your_openai_api_key
GOOGLE_PLACES_API_KEY=your_google_places_api_key
```

Start the backend:

```powershell
uvicorn app:app --reload
```

The local backend will run at:

```text
http://127.0.0.1:8000
```

## Render Deployment Settings

The backend was deployed on Render with these settings:

```text
Language: Python 3
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
```

The backend file is:

```text
backend/app.py
```

The FastAPI app object is:

```python
app
```

That is why the start command uses:

```text
uvicorn app:app
```

## Security

API keys are not stored in the frontend and are not uploaded to GitHub.

The following files are ignored:

```text
.env
backend/.env
frontend/.env
.venv/
__pycache__/
*.pyc
```

This means the GitHub repository contains the source code and example environment files, but not the real secret keys.

## Main Features

* Search for restaurants and food spots
* Filter based on rating and popularity
* Find lesser-known local places
* Save favorite places
* View place details
* Backend API handling for external services
* Render-hosted backend for easier testing and delivery

## Technologies Used

### Frontend

* Python
* Kivy
* Requests
* python-dotenv

### Backend

* Python
* FastAPI
* Uvicorn
* OpenAI API
* Google Places API
* python-dotenv

## Notes for Examiner

The backend is already hosted on Render, so the frontend can be run locally without needing API keys on the examiner’s computer.

If the backend appears offline at first, just wait a bit. Render’s free tier may need time to wake up the service.
