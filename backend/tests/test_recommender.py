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


def test_external_movie_metadata_can_be_recommended():
    model = MovieRecommender(MOVIES)
    external = {
        "id": 999999,
        "title": "A space adventure",
        "overview": "A crew travels through space to save humanity from danger.",
        "genre_names": ["Science Fiction", "Adventure"],
        "keywords": "space exploration survival",
    }
    results = model.similar_movie(external, 5)
    assert results
    assert all(str(item["id"]) != "999999" for item in results)


def test_recommendation_results_are_unique():
    model = MovieRecommender(MOVIES)
    results = model.similar(str(MOVIES[0]["id"]), 10)
    ids = [str(item["id"]) for item in results]
    assert len(ids) == len(set(ids))
