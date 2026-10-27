from __future__ import annotations
import os
from pathlib import Path
from typing import Optional
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .catalog import MOVIES
from .recommender import MovieRecommender

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
TMDB_KEY = os.getenv("TMDB_API_KEY", "").strip()
TMDB_BASE = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p/w500"
TMDB_GENRES = {
    28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
    99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
    27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
    10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
}
app = FastAPI(title="CineGlow Movie API", version="1.0.0", description="Movie discovery and content-based ML recommendations")
origins = [os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"), "http://127.0.0.1:5173"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
recommender = MovieRecommender(MOVIES)
LOCAL_BY_ID = {str(m["id"]): m for m in MOVIES}

class PersonalizeRequest(BaseModel):
    genres: list[str] = Field(default_factory=list)
    liked_movie_ids: list[str] = Field(default_factory=list)
    limit: int = Field(default=10, ge=1, le=20)

def normalize_tmdb(m: dict) -> dict:
    genre_names = m.get("genre_names")
    if not genre_names:
        genre_names = [g.get("name", "") for g in m.get("genres", []) if isinstance(g, dict)]
    if not genre_names:
        genre_names = [TMDB_GENRES[g] for g in m.get("genre_ids", []) if g in TMDB_GENRES]
    return {
        "id": m.get("id"), "title": m.get("title") or m.get("name") or "Untitled",
        "release_date": m.get("release_date") or "", "year": (m.get("release_date") or "")[:4] or None,
        "genres": genre_names, "genre_names": genre_names, "overview": m.get("overview") or "",
        "rating": m.get("vote_average"), "poster_path": (IMG_BASE + m["poster_path"]) if m.get("poster_path") else None,
        "backdrop_path": ("https://image.tmdb.org/t/p/w1280" + m["backdrop_path"]) if m.get("backdrop_path") else None,
        "runtime": m.get("runtime"), "credits": m.get("credits", {}), "videos": m.get("videos", {}),
        "source": "tmdb"
    }

async def tmdb(path: str, params: dict | None = None):
    if not TMDB_KEY:
        return None
    query = dict(params or {})
    query["api_key"] = TMDB_KEY
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(f"{TMDB_BASE}{path}", params=query)
            response.raise_for_status()
            return response.json()
    except (httpx.HTTPError, ValueError):
        return None

def local_filter(genre: Optional[str] = None, q: Optional[str] = None):
    items = MOVIES
    aliases = {"sci-fi": "science fiction", "sci fi": "science fiction", "scifi": "science fiction"}
    wanted = aliases.get((genre or "").strip().lower(), (genre or "").strip().lower())
    if wanted and wanted not in ("all", "all movies"):
        items = [m for m in items if wanted in [g.lower() for g in m.get("genre_names", m.get("genres", []))]]
    if q:
        needle = q.casefold().strip()
        items = [m for m in items if needle in m["title"].casefold() or needle in (m.get("overview") or "").casefold()]
    return items

@app.get("/api/health")
def health():
    return {"status": "ok", "ml_model": "TF-IDF + cosine similarity", "tmdb_enabled": bool(TMDB_KEY), "catalog_size": len(MOVIES)}

@app.get("/api/movies/genres")
def genres():
    return {"genres": sorted({g for m in MOVIES for g in m["genre_names"]})}

@app.get("/api/movies/trending")
async def trending():
    data = await tmdb("/trending/movie/week")
    return {"items": [normalize_tmdb(m) for m in data.get("results", [])[:20]], "source": "tmdb"} if data else {"items": MOVIES[:12], "source": "curated-local"}

@app.get("/api/movies/popular")
async def popular():
    data = await tmdb("/movie/popular")
    return {"items": [normalize_tmdb(m) for m in data.get("results", [])[:20]], "source": "tmdb"} if data else {"items": MOVIES[12:24], "source": "curated-local"}

@app.get("/api/movies/top-rated")
async def top_rated():
    data = await tmdb("/movie/top_rated")
    return {"items": [normalize_tmdb(m) for m in data.get("results", [])[:20]], "source": "tmdb"} if data else {"items": MOVIES[24:36], "source": "curated-local"}

@app.get("/api/movies/search")
async def search(q: str = Query(min_length=1, max_length=100)):
    data = await tmdb("/search/movie", {"query": q, "include_adult": "false"})
    if data:
        return {"items": [normalize_tmdb(m) for m in data.get("results", [])[:20]], "source": "tmdb"}
    return {"items": local_filter(q=q)[:20], "source": "curated-local"}

@app.get("/api/movies")
async def movies(genre: Optional[str] = None, q: Optional[str] = Query(default=None, max_length=100), page: int = Query(default=1, ge=1)):
    # Local catalog filtering is deterministic and remains available without a key.
    items = local_filter(genre=genre, q=q)
    start = (page - 1) * 100
    return {"items": items[start:start + 100], "total": len(items), "page": page, "source": "curated-local"}

@app.get("/api/movies/{movie_id}")
async def movie_detail(movie_id: str):
    if movie_id in LOCAL_BY_ID:
        return LOCAL_BY_ID[movie_id]
    data = await tmdb(f"/movie/{movie_id}", {"append_to_response": "credits,videos"})
    if data:
        return normalize_tmdb(data)
    raise HTTPException(status_code=404, detail="Movie not found. Configure TMDB_API_KEY for the wider movie catalog.")

@app.get("/api/recommendations/{movie_id}")
def recommendations(movie_id: str, limit: int = Query(default=10, ge=1, le=20)):
    if movie_id not in LOCAL_BY_ID:
        raise HTTPException(status_code=404, detail="This movie is not in the local ML catalog. Try a movie from the starter catalog.")
    return {"items": recommender.similar(movie_id, limit), "algorithm": "TF-IDF + cosine similarity"}

@app.post("/api/recommendations/personalized")
def personalized(payload: PersonalizeRequest):
    if not payload.genres and not payload.liked_movie_ids:
        raise HTTPException(status_code=400, detail="Choose at least one genre or liked movie first.")
    return {"items": recommender.personalized(payload.genres, payload.liked_movie_ids, payload.limit), "algorithm": "content-based preference profile"}
