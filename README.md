# CineGlow — Movie Discovery & Recommendation Platform

Discover your next favourite film with **CineGlow**, a responsive movie discovery website featuring search, genre filters, movie details, and content-based recommendations powered by machine learning.

CineGlow includes a **React + TypeScript** frontend and a **FastAPI** backend. Its recommendation engine uses **TF-IDF vectorization** and **cosine similarity** to find movies with related genres, descriptions, keywords, and titles. The app works with its bundled movie catalogue; an optional TMDB API key enables broader, live movie data.

---

## Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Run Locally](#run-locally)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Configure and Run the Backend](#2-configure-and-run-the-backend)
  - [3. Configure and Run the Frontend](#3-configure-and-run-the-frontend)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [How Recommendations Work](#how-recommendations-work)
- [Run Tests](#run-tests)
- [Production Build](#production-build)
- [Troubleshooting](#troubleshooting)
- [Data and Attribution](#data-and-attribution)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Movie discovery:** Browse curated movie collections for trending-style, popular, and top-rated sections.
- **Search:** Find movies by title or overview text.
- **Genre filtering:** Explore the catalogue by genre.
- **Movie details:** View available information for a selected movie.
- **Similar-movie recommendations:** Get suggestions based on a selected movie's metadata.
- **Personalized recommendations:** Build a preference profile using selected genres and liked movie IDs.
- **Content-based ML:** Rank films using TF-IDF features and cosine similarity.
- **Optional TMDB integration:** Use The Movie Database (TMDB) for expanded search, details, and live collections when an API key is configured.
- **Responsive interface:** React, TypeScript, and custom CSS with a CineGlow visual style.
- **API documentation:** Explore and test backend endpoints through FastAPI's interactive Swagger UI.

> **Offline-data note:** Without a TMDB API key, CineGlow uses its bundled starter catalogue. In this mode, the home collections are curated local selections rather than live trending or popular results.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite, CSS |
| UI and animation | Lucide React, Framer Motion |
| Backend | Python, FastAPI, Uvicorn |
| Machine learning | scikit-learn, TF-IDF, cosine similarity |
| Data processing | pandas, NumPy |
| HTTP and configuration | HTTPX, python-dotenv |
| Optional movie data provider | TMDB API |

## Project Structure

```text
movie-suggestion-website/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI application and API routes
│   │   ├── catalog.py        # Bundled starter movie catalogue
│   │   └── recommender.py    # TF-IDF and cosine-similarity logic
│   ├── tests/
│   │   └── test_recommender.py
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # Main React interface
│   │   ├── api.ts            # Backend API client
│   │   ├── main.tsx          # Frontend entry point
│   │   ├── types.ts          # TypeScript data types
│   │   └── styles.css        # Application styles
│   ├── .env.example
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── .gitignore
└── README.md
```

## Requirements

Install the following before starting:

- **Python 3.10 or newer**
- **Node.js 18 or newer** and npm
- **Git** (for cloning the repository)
- A terminal such as PowerShell, Windows Terminal, macOS Terminal, or a Linux shell
- **Optional:** A TMDB API key for expanded/live movie data

## Run Locally

Run the backend and frontend in **separate terminals**. Keep both terminals open while using the application.

### 1. Clone the Repository

Replace the example URL with your GitHub repository URL after you publish the project.

```bash
git clone https://github.com/YOUR-USERNAME/movie-suggestion-website.git
cd movie-suggestion-website
```

If you already have the project on your computer, open a terminal in the project root instead.

### 2. Configure and Run the Backend

#### Windows PowerShell

From the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

If PowerShell blocks virtual-environment activation, you can allow it for the current terminal session with:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This policy change applies only to the current PowerShell process. Alternatively, use Command Prompt and activate with `.venv\Scripts\activate.bat`.

#### macOS / Linux

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload --port 8000
```

The backend should be available at:

- API base: <http://127.0.0.1:8000>
- Interactive API docs: <http://127.0.0.1:8000/docs>
- Alternative API docs: <http://127.0.0.1:8000/redoc>
- Health check: <http://127.0.0.1:8000/api/health>

**Important:** The correct Uvicorn target is `app.main:app` because the FastAPI application is defined in `backend/app/main.py`.

### 3. Configure and Run the Frontend

Open a **second terminal** at the project root.

#### Windows PowerShell

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

#### macOS / Linux

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open the local address printed by Vite, normally <http://localhost:5173>.

The frontend environment file defaults to the local backend API. If you change the backend address or port, update `VITE_API_URL` in `frontend/.env` to match.

### 4. Optional: Enable TMDB Data

CineGlow can use a TMDB API key to retrieve broader movie data. Without a key, the bundled catalogue remains available.

1. Create a TMDB account and request an API key through TMDB's official developer process.
2. Open `backend/.env`.
3. Set the following values:

   ```env
   TMDB_API_KEY=your_tmdb_api_key
   FRONTEND_ORIGIN=http://localhost:5173
   ```

4. Restart the backend.

Keep your TMDB key in `backend/.env` only. **Never commit real API keys or secrets to GitHub.** The backend loads this file, and `.env` files are excluded by `.gitignore`.

## Environment Variables

### Backend — `backend/.env`

| Variable | Required | Default | Description |
|---|---|---|---|
| `TMDB_API_KEY` | No | Empty | Enables optional TMDB requests when configured. |
| `FRONTEND_ORIGIN` | No | `http://localhost:5173` | Frontend origin allowed by the backend's CORS configuration. |

Example:

```env
TMDB_API_KEY=
FRONTEND_ORIGIN=http://localhost:5173
```

### Frontend — `frontend/.env`

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_URL` | No | `http://localhost:8000/api` | Base URL for the backend API, including `/api`. |

Example:

```env
VITE_API_URL=http://localhost:8000/api
```

Vite exposes variables prefixed with `VITE_` to browser code. Do not put private keys or secrets in frontend environment variables.

## API Reference

The local API base URL is `http://127.0.0.1:8000/api`.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Reports API status, ML model, TMDB status, and local catalogue size. |
| `GET` | `/movies/genres` | Returns the available genres in the bundled catalogue. |
| `GET` | `/movies/trending` | Returns TMDB weekly trending results when enabled; otherwise a curated local collection. |
| `GET` | `/movies/popular` | Returns TMDB popular results when enabled; otherwise a curated local collection. |
| `GET` | `/movies/top-rated` | Returns TMDB top-rated results when enabled; otherwise a curated local collection. |
| `GET` | `/movies/search?q={query}` | Searches movie titles and overviews; uses TMDB when available. |
| `GET` | `/movies?genre={genre}&q={query}&page={page}` | Filters and paginates the bundled local catalogue. Parameters are optional. |
| `GET` | `/movies/{movie_id}` | Returns details for a local movie or requests details from TMDB when configured. |
| `GET` | `/recommendations/{movie_id}?limit=10` | Returns movies similar to a movie in the local ML catalogue. `limit` can be from 1 to 20. |
| `POST` | `/recommendations/personalized` | Returns recommendations based on selected genres and/or liked movie IDs. |

### Personalized recommendation request example

`POST /api/recommendations/personalized`

```json
{
  "genres": ["Science Fiction", "Adventure"],
  "liked_movie_ids": ["1", "2"],
  "limit": 10
}
```

Provide at least one genre or liked movie ID. The `limit` must be between 1 and 20. Movie IDs must match entries in the bundled catalogue to contribute to the local recommendation model.

For request and response schemas, use the interactive documentation at <http://127.0.0.1:8000/docs> while the backend is running.

## How Recommendations Work

CineGlow uses **content-based filtering** rather than collaborative filtering:

1. The recommender combines each movie's genres, overview, keywords, and title into a text representation.
2. `TfidfVectorizer` converts the text into weighted numerical features, ignoring common English stop words and considering single words and two-word phrases.
3. Cosine similarity compares the feature vectors and estimates how closely movies match.
4. Similar-movie recommendations rank the closest catalogue entries and exclude the selected movie itself.
5. Personalized recommendations score catalogue entries against selected genres and liked movies.

The model is initialized from the bundled catalogue. TMDB can supply expanded movie information, but movies returned only by TMDB are not automatically part of the local recommendation model.

## Run Tests

Run backend tests from the `backend` directory with the virtual environment activated:

```bash
python -m pytest
```

To run the frontend's TypeScript check and production build, run from the `frontend` directory:

```bash
npm run build
```

## Production Build

Create a production frontend build from the `frontend` directory:

```bash
npm run build
```

Vite writes the built frontend to `frontend/dist/`. To preview that build locally:

```bash
npm run preview
```

The FastAPI development command with `--reload` is intended for local development, not production deployment. For deployment, host the frontend and backend using your preferred providers, configure `VITE_API_URL` to the deployed API URL, set `FRONTEND_ORIGIN` to the deployed frontend origin, and store `TMDB_API_KEY` as a server-side secret if used. Configure HTTPS and CORS for your deployment environment.

## Troubleshooting

### `Could not import module "main"` or `Could not import module "api"`

Run the backend command from the `backend` directory and use the correct module path:

```powershell
python -m uvicorn app.main:app --reload --port 8000
```

### `ModuleNotFoundError` when starting the backend

Activate the backend virtual environment and install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Frontend cannot connect to the API

- Confirm the backend is running at `http://127.0.0.1:8000`.
- Open <http://127.0.0.1:8000/api/health> to check the API.
- Check `frontend/.env` and confirm `VITE_API_URL=http://localhost:8000/api`.
- Restart the Vite development server after changing environment variables.
- If using another host or port, update the backend CORS origin and the frontend API URL accordingly.

### TMDB data is unavailable

- Check that `TMDB_API_KEY` is set correctly in `backend/.env`.
- Restart the backend after changing the key.
- If TMDB is unavailable or the request fails, the API may fall back to the bundled catalogue for supported collection and search endpoints.

### Port `8000` or `5173` is already in use

Stop the process using the port or choose another port. If you change the backend port, update `VITE_API_URL` in `frontend/.env` to match.

## Data and Attribution

- The bundled starter catalogue is used by the local recommendation engine.
- TMDB integration is optional and subject to [TMDB's terms of use](https://www.themoviedb.org/terms-of-use) and [API documentation](https://developer.themoviedb.org/docs). If you use TMDB data publicly, follow its current attribution and branding requirements.
- CineGlow is an independent project and is not endorsed, certified, or sponsored by TMDB.
- Movie poster and backdrop images may be served by TMDB when that integration is enabled; their availability is controlled by the provider.

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Make and test your changes.
4. Commit your work: `git commit -m "Add your feature"`.
5. Push the branch and open a pull request.

Please avoid committing `.env` files, API keys, virtual environments, `node_modules`, or build output.

## License

No license file is currently included. Unless a license is added to the repository, all rights remain with the copyright holder and reuse is not automatically granted. Add a `LICENSE` file before publishing the project if you want to specify reuse permissions.
