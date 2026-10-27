from __future__ import annotations
from typing import Iterable
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MovieRecommender:
    """Content-based movie recommender using TF-IDF and cosine similarity."""
    def __init__(self, movies: list[dict]):
        self.movies = movies
        self.by_id = {str(m["id"]): i for i, m in enumerate(movies)}
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), min_df=1)
        self.matrix = self.vectorizer.fit_transform([self._text(m) for m in movies])
        self.similarity = cosine_similarity(self.matrix, dense_output=True)

    @staticmethod
    def _text(movie: dict) -> str:
        genres = movie.get("genre_names") or movie.get("genres") or []
        if genres and isinstance(genres[0], dict):
            genres = [g.get("name", "") for g in genres]
        return " ".join([
            " ".join(str(g) for g in genres),
            str(movie.get("overview") or ""),
            str(movie.get("keywords") or ""),
            str(movie.get("title") or "")
        ])

    def similar(self, movie_id: str | int, limit: int = 10) -> list[dict]:
        idx = self.by_id.get(str(movie_id))
        if idx is None:
            return []
        scores = self.similarity[idx]
        ranked = sorted(range(len(self.movies)), key=lambda i: float(scores[i]), reverse=True)
        results = []
        for i in ranked:
            if i == idx or float(scores[i]) <= 0:
                continue
            item = dict(self.movies[i])
            item["similarity"] = round(float(scores[i]), 4)
            item["recommendation_reason"] = self._reason(self.movies[idx], self.movies[i])
            results.append(item)
            if len(results) >= limit:
                break
        return results

    def personalized(self, genres: Iterable[str], liked_ids: Iterable[str | int], limit: int = 10) -> list[dict]:
        genre_set = {str(g).strip().lower() for g in genres if str(g).strip()}
        liked_indices = [self.by_id[str(mid)] for mid in liked_ids if str(mid) in self.by_id]
        if not genre_set and not liked_indices:
            return []
        scores = []
        for i, movie in enumerate(self.movies):
            if i in liked_indices:
                continue
            movie_genres = {str(g).lower() for g in (movie.get("genre_names") or movie.get("genres") or [])}
            genre_score = len(genre_set & movie_genres) / max(len(genre_set), 1) if genre_set else 0
            liked_score = max((float(self.similarity[i][j]) for j in liked_indices), default=0)
            score = (0.65 * genre_score + 0.35 * liked_score) if genre_set and liked_indices else (genre_score if genre_set else liked_score)
            if score > 0:
                item = dict(movie)
                item["similarity"] = round(float(score), 4)
                item["recommendation_reason"] = "Matches your selected genres and movie interests"
                scores.append(item)
        return sorted(scores, key=lambda m: m["similarity"], reverse=True)[:limit]

    @staticmethod
    def _reason(source: dict, target: dict) -> str:
        a = {str(g).lower() for g in (source.get("genre_names") or source.get("genres") or [])}
        b = {str(g).lower() for g in (target.get("genre_names") or target.get("genres") or [])}
        shared = sorted(a & b)
        return ("Similar genres: " + ", ".join(shared[:3])) if shared else "Similar story themes and movie metadata"
