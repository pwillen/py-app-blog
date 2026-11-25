"""
MusicBrainz service
"""

import httpx
from django.conf import settings
from pydantic import BaseModel, Field, field_validator


class MusicBrainzArtist(BaseModel, extra="ignore"):
    id: str
    name: str


class MusicBrainzArtistCredit(BaseModel, extra="ignore"):
    artist: MusicBrainzArtist
    name: str | None = None
    joinphrase: str | None = None


class MusicBrainzReleaseGroup(BaseModel, extra="ignore"):
    id: str
    title: str
    release_year: int | None = Field(
        default=None,
        validation_alias="first-release-date",
    )
    artist_credit: list[MusicBrainzArtistCredit] = Field(
        default_factory=list,
        alias="artist-credit",
    )

    @property
    def artist_name(self) -> str:
        """
        Concatenates the names of the artists with their join phrases in the
        artist_credit list.
        Returns: The concatenated artist names.

        """
        return "".join(
            (credit.name or "") + (credit.joinphrase or "")
            for credit in self.artist_credit
        )

    @field_validator("release_year", mode="before")
    @classmethod
    def extract_release_year(cls, value: str | None) -> int | None:
        """
        Extracts the release year from the first four characters of the
        first-release-date string.
        Args:
            value: The first-release-date string.

        Returns: The release year as an integer, or None if it cannot be determined.

        """
        if not value:
            return None

        year = value[:4]

        return int(year) if year.isdigit() else None


class MusicBrainzSearchResponse(BaseModel, extra="ignore"):
    count: int
    offset: int
    release_groups: list[MusicBrainzReleaseGroup] = Field(
        alias="release-groups",
    )


class MusicBrainzClient:
    """
    Client for interacting with the MusicBrainz API.
    """

    BASE_URL = "https://musicbrainz.org/ws/2"

    def __init__(self):
        self.client = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "User-Agent": settings.API_USER_AGENT,
                "Accept": "application/json",
            },
            timeout=10,
        )

    def search_release_groups(
        self,
        query: str,
    ) -> MusicBrainzSearchResponse:
        """
        Search for release groups in MusicBrainz.
        Args:
            query: The search query string.

        Returns: MusicBrainz API response validated as MusicBrainzSearchResponse

        """
        response = self.client.get(
            "/release-group",
            params={
                "query": query,
                "fmt": "json",
                "limit": 10,
            },
        )
        response.raise_for_status()

        return MusicBrainzSearchResponse.model_validate(response.json())

    def get_release_group(
        self,
        release_group_id: str,
    ) -> MusicBrainzReleaseGroup:
        """
        Retrieve a release group by its MusicBrainz ID.
        Args:
            release_group_id: The MusicBrainz ID of the release group.
        Returns: The MusicBrainzReleaseGroup object.
        """
        response = self.client.get(
            f"/release-group/{release_group_id}",
            params={
                "fmt": "json",
                "inc": "artist-credits",
            },
        )
        response.raise_for_status()

        return MusicBrainzReleaseGroup.model_validate(response.json())

    def get_cover_art_url(self, release_group_id: str) -> str | None:
        """
        Retrieve the 500px front cover URL for a release group.
        """

        # Use httpx.get instead of self.client.get to avoid the base URL being
        # prepended.
        response = httpx.get(
            f"https://coverartarchive.org/release-group/{release_group_id}",
            headers={
                "User-Agent": settings.API_USER_AGENT,
                "Accept": "application/json",
            },
            timeout=10,
            follow_redirects=True,
        )

        if response.status_code == 404:
            return None

        response.raise_for_status()

        images = response.json().get("images", [])

        # Find the front cover image in the list of images by checking the "front" key.
        front_cover = next(
            (image for image in images if image.get("front")),
            None,
        )

        if not front_cover:
            return None

        thumbnails = front_cover.get("thumbnails", {})

        return thumbnails.get("500") or front_cover.get("image")

    def close(self):
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
