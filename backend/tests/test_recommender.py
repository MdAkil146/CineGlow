from app.catalog import MOVIES
from app.recommender import MovieRecommender

def test_recommendations_exclude_selected_movie():
    model = MovieRecommender(MOVIES)
    selected = str(MOVIES[0]["id"])
    results = model.similar(selected, 10)
    assert all(str(m["id"]) != selected for m in results)
    assert len(results) > 0

def test_personalized_requires_preferences():
    model = MovieRecommender(MOVIES)
    assert model.personalized([], [], 10) == []

def test_genre_personalization_returns_matching_items():
    model = MovieRecommender(MOVIES)
    results = model.personalized(["Animation"], [], 10)
    assert results
    assert all("Animation" in m["genre_names"] for m in results)
