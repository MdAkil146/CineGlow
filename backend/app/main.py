from __future__ import annotations

import os
import time
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
GENRE_IDS = {name.casefold(): key for key, name in TMDB_GENRES.items()}
GENRE_IDS.update({"sci-fi": 878, "sci fi": 878, "scifi": 878})

app = FastAPI(
    title="CineGlow Movie API",
    version="1.1.0",
    description="Movie discovery with resilient TMDB integration and content-based ML recommendations",
)
origins = [os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"), "http://127.0.0.1:5173"]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

recommender = MovieRecommender(MOVIES)
LOCAL_BY_ID = {str(m["id"]): m for m in MOVIES}
# Small in-process cache: avoids repeated calls and keeps the app usable during brief TMDB outages.
_CACHE: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 300
CACHE_MAX = 256


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
    release_date = m.get("release_date") or ""
    poster_path = m.get("poster_path")
    backdrop_path = m.get("backdrop_path")
    return {
        "id": m.get("id"),
        "title": m.get("title") or m.get("name") or "Untitled",
        "release_date": release_date,
        "year": release_date[:4] or None,
        "genres": genre_names,
        "genre_names": genre_names,
        "overview": m.get("overview") or "",
        "rating": m.get("vote_average"),
        "poster_path": (IMG_BASE + poster_path) if poster_path else None,
        "backdrop_path": ("https://image.tmdb.org/t/p/w1280" + backdrop_path) if backdrop_path else None,
        "runtime": m.get("runtime"),
        "credits": m.get("credits", {}),
        "videos": m.get("videos", {}),
        "source": "tmdb",
    }


async def tmdb(path: str, params: dict | None = None):
    """Return cached TMDB JSON, or None on missing key/provider/network errors."""
    if not TMDB_KEY:
        return None
    query = dict(params or {})
    query["api_key"] = TMDB_KEY
    cache_key = path + "?" + "&".join(f"{k}={v}" for k, v in sorted(query.items()))
    now = time.monotonic()
    cached = _CACHE.get(cache_key)
    if cached and now - cached[0] < CACHE_TTL:
        return cached[1]
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(7.0, connect=3.0)) as client:
            response = await client.get(f"{TMDB_BASE}{path}", params=query)
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                if len(_CACHE) >= CACHE_MAX:
                    oldest = min(_CACHE, key=lambda key: _CACHE[key][0])
                    _CACHE.pop(oldest, None)
                _CACHE[cache_key] = (now, payload)
            return payload
    except (httpx.HTTPError, ValueError):
        # A provider outage must not take down local catalogue/search/recommendations.
        return cached[1] if cached else None


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


def unique_movies(items: list[dict]) -> list[dict]:
    seen, result = set(), []
    for item in items:
        key = str(item.get("id") or item.get("title", "")).casefold()
        if key and key not in seen:
            seen.add(key)
            result.append(item)
    return result


def paged(items: list[dict], page: int, per_page: int = 20):
    start = (page - 1) * per_page
    return {
        "items": items[start:start + per_page],
        "page": page,
        "total": len(items),
        "total_pages": max(1, (len(items) + per_page - 1) // per_page),
    }


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "ml_model": "TF-IDF + cosine similarity + diversity reranking",
        "tmdb_enabled": bool(TMDB_KEY),
        "catalog_size": len(MOVIES),
        "fallback_available": True,
    }


@app.get("/api/movies/genres")
def genres():
    return {"genres": sorted({g for m in MOVIES for g in m["genre_names"]})}


@app.get("/api/movies/trending")
async def trending(page: int = Query(default=1, ge=1, le=500)):
    data = await tmdb("/trending/movie/week", {"page": page})
    if data and data.get("results"):
        return {**paged([normalize_tmdb(m) for m in data["results"]], 1), "page": page,
                "total": data.get("total_results", len(data["results"])),
                "total_pages": data.get("total_pages", 1), "source": "tmdb"}
    return {**paged(MOVIES[:12] if page == 1 else [], 1), "source": "curated-local"}


@app.get("/api/movies/popular")
async def popular(page: int = Query(default=1, ge=1, le=500)):
    data = await tmdb("/movie/popular", {"page": page})
    if data and data.get("results"):
        return {"items": [normalize_tmdb(m) for m in data["results"]], "page": page,
                "total": data.get("total_results", 0), "total_pages": data.get("total_pages", 1), "source": "tmdb"}
    return {**paged(MOVIES[12:24] if page == 1 else [], 1), "source": "curated-local"}


@app.get("/api/movies/top-rated")
async def top_rated(page: int = Query(default=1, ge=1, le=500)):
    data = await tmdb("/movie/top_rated", {"page": page})
    if data and data.get("results"):
        return {"items": [normalize_tmdb(m) for m in data["results"]], "page": page,
                "total": data.get("total_results", 0), "total_pages": data.get("total_pages", 1), "source": "tmdb"}
    return {**paged(MOVIES[24:36] if page == 1 else [], 1), "source": "curated-local"}


@app.get("/api/movies/search")
async def search(
    q: str = Query(min_length=1, max_length=100),
    page: int = Query(default=1, ge=1, le=500),
    genre: Optional[str] = None,
):
    params = {"query": q, "include_adult": "false", "page": page}
    data = await tmdb("/search/movie", params)
    if data and data.get("results") is not None:
        remote = [normalize_tmdb(m) for m in data["results"]]
        if genre and genre.casefold() not in ("all", "all movies"):
            wanted = "science fiction" if genre.casefold() in ("sci-fi", "sci fi", "scifi") else genre.casefold()
            remote = [m for m in remote if wanted in [g.casefold() for g in m["genre_names"]]]
        # Include local matches on the first page, without duplicating TMDB titles.
        if page == 1:
            remote = unique_movies(remote + local_filter(genre=genre, q=q))
        return {"items": remote, "page": page, "total": data.get("total_results", len(remote)),
                "total_pages": data.get("total_pages", 1), "source": "tmdb+local"}
    local = local_filter(genre=genre, q=q)
    return {**paged(local, page), "source": "curated-local"}


@app.get("/api/movies")
async def movies(
    genre: Optional[str] = None,
    q: Optional[str] = Query(default=None, max_length=100),
    page: int = Query(default=1, ge=1, le=500),
):
    # TMDB discover broadens genre browsing; local results remain available as a fallback.
    if genre and genre.casefold() not in ("all", "all movies"):
        genre_id = GENRE_IDS.get(genre.casefold())
        if genre_id:
            data = await tmdb("/discover/movie", {
                "with_genres": genre_id, "sort_by": "popularity.desc",
                "include_adult": "false", "page": page,
            })
            if data and data.get("results") is not None:
                remote = [normalize_tmdb(m) for m in data["results"]]
                if q:
                    needle = q.casefold()
                    remote = [m for m in remote if needle in m["title"].casefold() or needle in m["overview"].casefold()]
                return {"items": remote, "total": data.get("total_results", len(remote)),
                        "page": page, "total_pages": data.get("total_pages", 1), "source": "tmdb"}
    local = local_filter(genre=genre, q=q)
    return {**paged(local, page, 100), "source": "curated-local"}


@app.get("/api/movies/{movie_id}")
async def movie_detail(movie_id: str):
    if movie_id in LOCAL_BY_ID:
        return LOCAL_BY_ID[movie_id]
    data = await tmdb(f"/movie/{movie_id}", {"append_to_response": "credits,videos"})
    if data:
        return normalize_tmdb(data)
    raise HTTPException(status_code=404, detail="Movie details are unavailable. Check your connection or TMDB configuration.")


@app.get("/api/recommendations/{movie_id}")
async def recommendations(movie_id: str, limit: int = Query(default=10, ge=1, le=20)):
    local = LOCAL_BY_ID.get(movie_id)
    if local:
        return {"items": recommender.similar(movie_id, limit), "algorithm": "TF-IDF + cosine similarity + diversity"}
    external = await tmdb(f"/movie/{movie_id}", {"append_to_response": "credits"})
    if not external:
        raise HTTPException(status_code=404, detail="This movie is not in the local ML catalogue and its TMDB metadata could not be fetched.")
    query_movie = normalize_tmdb(external)
    credits = external.get("credits") or {}
    query_movie["cast"] = [person.get("name", "") for person in credits.get("cast", [])[:8]]
    crew = credits.get("crew", [])
    query_movie["director"] = next((person.get("name", "") for person in crew if person.get("job") == "Director"), "")
    return {"items": recommender.similar_movie(query_movie, limit),
            "algorithm": "TF-IDF content matching + diversity",
            "note": "External movie metadata is compared against the bundled ML catalogue."}


@app.post("/api/recommendations/personalized")
def personalized(payload: PersonalizeRequest):
    if not payload.genres and not payload.liked_movie_ids:
        raise HTTPException(status_code=400, detail="Choose at least one genre or liked movie first.")
    return {"items": recommender.personalized(payload.genres, payload.liked_movie_ids, payload.limit),
            "algorithm": "content-based preference profile + diversity"}
