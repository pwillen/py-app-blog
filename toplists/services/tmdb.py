import httpx

from django.conf import settings
from pydantic import BaseModel, ConfigDict


class TMDBMovie(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    title: str
    release_date: str | None = None
    poster_path: str | None = None
    overview: str | None = None


class TMDBSearchResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    page: int
    results: list[TMDBMovie]
    total_pages: int
    total_results: int


class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        token = settings.TMDB_API_READ_ACCESS_TOKEN

        if not token:
            raise ValueError("TMDB API token is not configured.")

        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
            },
            timeout=10,
        )

    def search_movies(self, query: str) -> TMDBSearchResponse:
        response = self.client.get(
            "/search/movie",
            params={
                "query": query,
                "include_adult": False,
            },
        )
        response.raise_for_status()

        return TMDBSearchResponse.model_validate(response.json())

    def get_movie(self, tmdb_id: int) -> TMDBMovie:
        response = self.client.get(f"/movie/{tmdb_id}")
        response.raise_for_status()

        return TMDBMovie.model_validate(response.json())

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()