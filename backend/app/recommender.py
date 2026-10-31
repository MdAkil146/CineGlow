from __future__ import annotations

from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MovieRecommender:
    """Content-based TF-IDF recommender with lightweight diversity reranking."""

    def __init__(self, movies: list[dict]):
        self.movies = movies
        self.by_id = {str(m["id"]): i for i, m in enumerate(movies)}
        self.vectorizer = TfidfVectorizer(
            stop_words="english", ngram_range=(1, 2), min_df=1,
            max_features=150_000, sublinear_tf=True,
        )
        # Keep the feature matrix sparse. A dense N x N similarity matrix becomes
        # unnecessarily expensive as the movie catalogue grows.
        self.matrix = self.vectorizer.fit_transform([self._text(m) for m in movies])

    @staticmethod
    def _text(movie: dict) -> str:
        genres = movie.get("genre_names") or movie.get("genres") or []
        if genres and isinstance(genres[0], dict):
            genres = [g.get("name", "") for g in genres]
        keywords = movie.get("keywords") or ""
        if isinstance(keywords, list):
            keywords = " ".join(str(k) for k in keywords)
        cast = movie.get("cast") or movie.get("credits", {}).get("cast", [])
        if isinstance(cast, list):
            cast = " ".join(
                str(x.get("name", "")) if isinstance(x, dict) else str(x)
                for x in cast[:8]
            )
        director = movie.get("director") or ""
        return " ".join([
            str(movie.get("title") or ""),
            " ".join(str(g) for g in genres),
            str(movie.get("overview") or ""),
            str(keywords),
            str(cast),
            str(director),
        ])

    @staticmethod
    def _genres(movie: dict) -> set[str]:
        values = movie.get("genre_names") or movie.get("genres") or []
        if values and isinstance(values[0], dict):
            values = [g.get("name", "") for g in values]
        return {str(g).casefold() for g in values if str(g).strip()}

    def _diverse(self, candidates: list[tuple[int, float]], limit: int) -> list[tuple[int, float]]:
        """Greedy relevance/diversity ranking; avoids returning one near-identical cluster."""
        chosen: list[tuple[int, float]] = []
        remaining = candidates[:]
        while remaining and len(chosen) < limit:
            best_pos, best_value = 0, float("-inf")
            for pos, (idx, relevance) in enumerate(remaining):
                candidate_genres = self._genres(self.movies[idx])
                if not chosen:
                    diversity = 1.0
                else:
                    overlap = [
                        len(candidate_genres & self._genres(self.movies[old_idx]))
                        / max(len(candidate_genres | self._genres(self.movies[old_idx])), 1)
                        for old_idx, _ in chosen
                    ]
                    diversity = 1.0 - max(overlap, default=0.0)
                score = 0.82 * relevance + 0.18 * diversity
                if score > best_value:
                    best_pos, best_value = pos, score
            chosen.append(remaining.pop(best_pos))
        return chosen

    def similar(self, movie_id: str | int, limit: int = 10) -> list[dict]:
        idx = self.by_id.get(str(movie_id))
        if idx is None:
            return []
        scores = cosine_similarity(self.matrix[idx], self.matrix).ravel()
        candidates = [
            (i, float(scores[i])) for i in range(len(self.movies))
            if i != idx and float(scores[i]) > 0
        ]
        candidates.sort(key=lambda item: item[1], reverse=True)
        results = []
        for i, score in self._diverse(candidates[:max(limit * 5, limit)], limit):
            item = dict(self.movies[i])
            item["similarity"] = round(score, 4)
            item["recommendation_reason"] = self._reason(self.movies[idx], self.movies[i])
            results.append(item)
        return results

    def similar_movie(self, movie: dict, limit: int = 10) -> list[dict]:
        """Compare an external movie's metadata with the local catalogue without persisting it."""
        query = self.vectorizer.transform([self._text(movie)])
        scores = cosine_similarity(query, self.matrix).ravel()
        candidates = [(i, float(score)) for i, score in enumerate(scores) if score > 0]
        candidates.sort(key=lambda item: item[1], reverse=True)
        results = []
        for i, score in self._diverse(candidates[:max(limit * 5, limit)], limit):
            item = dict(self.movies[i])
            item["similarity"] = round(score, 4)
            item["recommendation_reason"] = self._reason(movie, self.movies[i])
            results.append(item)
        return results

    def personalized(self, genres: Iterable[str], liked_ids: Iterable[str | int], limit: int = 10) -> list[dict]:
        aliases = {"sci-fi": "science fiction", "sci fi": "science fiction", "scifi": "science fiction"}
        genre_set = {
            aliases.get(str(g).strip().casefold(), str(g).strip().casefold())
            for g in genres if str(g).strip()
        }
        liked_indices = [self.by_id[str(mid)] for mid in liked_ids if str(mid) in self.by_id]
        if not genre_set and not liked_indices:
            return []

        candidates = []
        for i, movie in enumerate(self.movies):
            if i in liked_indices:
                continue
            movie_genres = self._genres(movie)
            genre_score = len(genre_set & movie_genres) / max(len(genre_set), 1) if genre_set else 0.0
            liked_score = 0.0
            if liked_indices:
                liked_score = max(
                    float(cosine_similarity(self.matrix[i], self.matrix[j]).ravel()[0])
                    for j in liked_indices
                )
            if genre_set and liked_indices:
                score = 0.55 * genre_score + 0.45 * liked_score
            else:
                score = genre_score if genre_set else liked_score
            if score > 0:
                candidates.append((i, float(score)))

        candidates.sort(key=lambda item: item[1], reverse=True)
        results = []
        for i, score in self._diverse(candidates[:max(limit * 5, limit)], limit):
            item = dict(self.movies[i])
            item["similarity"] = round(score, 4)
            item["recommendation_reason"] = "Matches your selected genres and movie interests"
            results.append(item)
        return results

    @staticmethod
    def _reason(source: dict, target: dict) -> str:
        shared = sorted(MovieRecommender._genres(source) & MovieRecommender._genres(target))
        return ("Similar genres: " + ", ".join(shared[:3])) if shared else "Similar story themes and movie metadata"
