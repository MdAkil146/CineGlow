# 🎬 CineGlow – AI/ML Movie Recommendation System

**Discover movies you'll love. Explore smarter. Get personalized recommendations.**

CineGlow is an AI/ML-powered movie discovery and recommendation web application developed as a Third-Year B.Tech Computer Science and Engineering project.

The application helps users discover movies, explore movie information, search for titles, and receive recommendations based on movie content and personal preferences.

It combines a **Content-Based Movie Recommendation System** using Machine Learning with movie data retrieved through The Movie Database (TMDB) API.

---

## ✨ Key Features

### 🎥 1. Movie Discovery
- Explore a collection of movies.
- Discover movies through genres.
- Browse movie information, ratings, descriptions, and posters.
- Explore movie results through paginated discovery.
- Load additional results when available.

### 🔍 2. Smart Movie Search
- Search for movies by title.
- Retrieve matching movie results using TMDB integration.
- Support local catalogue fallback when external movie data is unavailable.
- Explore a wider range of movies beyond the bundled catalogue.

### 🤖 3. AI/ML-Based Similar Movie Recommendations
CineGlow implements a Content-Based Filtering recommendation system.

When a user selects a movie, the recommendation engine identifies other movies with similar content.

The system uses:
- TF-IDF (Term Frequency–Inverse Document Frequency)
- Cosine Similarity
- Movie metadata such as genres, overview, keywords, and other available information.
- Recommendation ranking and diversity reranking.

### 💜 4. For You – Personalized Recommendations
The For You section helps users discover movies based on their preferences.

Personalization can use:
- Selected movie genres.
- Liked movies.
- Similarity-based recommendation logic.
- Preference-based ranking.

The recommendations are generated using the available movie metadata and user-provided preferences.

### 🗂️ 5. Movie Information
- Movie titles and descriptions.
- Genres and available metadata.
- Movie posters.
- Ratings and other available movie information.

### ⚡ 6. Performance Improvements
- Sparse TF-IDF matrix for efficient text-vector storage.
- Caching for repeated recommendation requests.
- Request timeouts and fallback handling.
- Paginated movie discovery to avoid loading all results at once.

---

## 🧠 Machine Learning Implementation

CineGlow uses a **Content-Based Filtering** approach.

### Technologies Used

| Technology | Purpose |
|---|---|
| Python | ML and backend development |
| Scikit-learn | Machine Learning implementation |
| TF-IDF Vectorizer | Converts movie text into numerical vectors |
| Cosine Similarity | Measures similarity between movie vectors |
| Sparse Matrix | Efficiently stores vectorized data |

### How the Recommendation System Works

1. **Movie Data Collection:** The system obtains available movie information, including titles, genres, descriptions, and keywords.
2. **Text Processing:** Relevant movie information is combined into textual features.
3. **TF-IDF Vectorization:** Textual features are converted into numerical vectors.
4. **Similarity Calculation:** Cosine Similarity measures the similarity between movies.
5. **Recommendation Ranking:** Movies are ranked according to their relevance.
6. **Diversity Reranking:** The results are adjusted to help reduce repetitive recommendations.
7. **Displaying Results:** Relevant movie recommendations are returned to the frontend.

### ML Workflow

```text
       Movie Dataset
             |
             v
      Text Processing
             |
             v
      TF-IDF Vectorizer
             |
             v
      Numerical Vectors
             |
             v
      Cosine Similarity
             |
             v
    Recommendation Ranking
             |
             v
     Diversity Reranking
             |
             v
   Recommended Movies
```

**Note:** CineGlow uses traditional Machine Learning techniques. It does not currently depend on deep learning or neural networks, and it does not continuously retrain itself from user activity.

---

## 🛠️ Technology Stack

### Frontend
- React
- TypeScript
- Vite
- Tailwind CSS
- Framer Motion
- Lucide React

### Backend
- Python
- FastAPI
- Uvicorn
- HTTPX
- Python-dotenv

### Machine Learning
- Scikit-learn
- TF-IDF Vectorization
- Cosine Similarity

### External API
- TMDB API – Movie information, posters, search, and discovery.

---

## 📁 Project Structure

```text
movie-suggestion-website/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── catalog.py
│   │   └── recommender.py
│   │
│   ├── tests/
│   │   └── test_recommender.py
│   │
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts
│   │   └── types.ts
│   │
│   ├── public/
│   ├── package.json
│   └── index.html
│
└── README.md
```

---

## ⚙️ Installation and Setup

Follow these instructions to run CineGlow locally.

### Prerequisites

Install the following:

- Python
- Node.js and npm
- Git
- A TMDB API key (optional, but required for live TMDB features)

### 1. Clone the Repository

```bash
git clone https://github.com/MdAkil146/CineGlow.git
```

Navigate to the project directory:

```bash
cd movie-suggestion-website
```

### 2. Backend Setup

Open a terminal:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the required dependencies:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file inside the `backend` folder.

Add the following:

```env
TMDB_API_KEY=your_actual_tmdb_api_key
FRONTEND_ORIGIN=http://localhost:5173
```

Replace `your_actual_tmdb_api_key` with your TMDB API key.

**Important:**
- Keep your API key private.
- Never upload your `.env` file to GitHub.
- Do not expose your TMDB API key in frontend code.

If you do not configure a TMDB API key, features dependent on live TMDB data may be unavailable. The local catalogue fallback can still be used where supported.

### 4. Start the Backend Server

From the `backend` directory:

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Backend server:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/api/health
```

### 5. Frontend Setup

Open a second terminal:

```bash
cd movie-suggestion-website/frontend
```

Install frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the website:

```text
http://localhost:5173
```

---

## 🔗 Backend API

The backend exposes API endpoints for application functionality.

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/health` | GET | Check backend health |
| `/api/recommendations/{movie_id}` | GET | Get similar movie recommendations |
| `/api/recommendations/personalized` | POST | Generate preference-based recommendations |

Interactive API documentation is available at:

**http://127.0.0.1:8000/docs**

---

## 🧪 Testing the Machine Learning System

You can test the recommendation functionality using the following scenarios:

**Test 1 – Similar Movies**
1. Open CineGlow.
2. Search for a movie.
3. Open its details.
4. Navigate to Similar Movies.
5. Check whether the recommended movies have relevant content.

**Test 2 – Different Movie Inputs**
1. Select a science-fiction movie.
2. Observe its recommendations.
3. Select a romance movie.
4. Compare the recommendations.

**Test 3 – For You**
1. Open the For You page.
2. Select your preferred genres.
3. Add liked movies if supported by the interface.
4. Observe whether the recommendations change.

**Test 4 – Backend API**
1. Open `http://127.0.0.1:8000/docs`.
2. Find the recommendation endpoints.
3. Execute a recommendation request.
4. Inspect the returned movie results.

---

## 🔐 API Key and Security

CineGlow uses environment variables to manage sensitive configuration.

- TMDB API credentials are stored in the backend `.env` file.
- The `.env` file should not be committed to Git.
- Use a `.gitignore` file to exclude sensitive configuration and generated files.

Example `.gitignore` entries:

```gitignore
.env
.venv/
__pycache__/
*.pyc
node_modules/
dist/
.pytest_cache/
```

If an API key is accidentally pushed to a public repository, revoke or rotate it.

---

## 🎯 Project Objectives

- Develop an intelligent movie recommendation application.
- Apply Machine Learning concepts to a real-world use case.
- Implement content-based filtering using TF-IDF and Cosine Similarity.
- Improve movie discovery through external API integration.
- Provide personalized movie recommendations.
- Combine frontend development, backend APIs, and Machine Learning into one application.

---

## 🚀 Future Enhancements

- User accounts and persistent preference storage.
- Watchlist and favourite movie management.
- Improved recommendation personalization.
- Collaborative Filtering using user interaction data.
- Hybrid Recommendation System combining content-based and collaborative approaches.
- Recommendation feedback and evaluation.
- Deployment to a cloud hosting platform.

---

## 👨‍💻 Project Information

**Project Name:** CineGlow – AI/ML Movie Recommendation System

**Project Type:** Academic Mini Project

**Department:** Computer Science and Engineering

**Academic Level:** Third-Year B.Tech

**Domain:** Artificial Intelligence and Machine Learning, Web Development

---

## 🙌 Acknowledgements

- [The Movie Database (TMDB)](https://www.themoviedb.org/) – Movie information and API services.
- [Scikit-learn](https://scikit-learn.org/) – Machine Learning tools.
- [FastAPI](https://fastapi.tiangolo.com/) – Backend framework.
- [React](https://react.dev/) – Frontend library.
- [Vite](https://vite.dev/) – Frontend development and build tooling.

---

**CineGlow – Discover Your Next Favourite Movie.** 🎬