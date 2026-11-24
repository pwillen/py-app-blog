"""
Django models for the Top Lists app.
"""
from django.db import models
from django.db.models import Q
from django.urls import reverse


# Movie Models
class Movie(models.Model):
    """
    Represents a movie in the database.
    """
    title = models.CharField(max_length=200)
    release_year = models.PositiveSmallIntegerField()
    # https://docs.djangoproject.com/en/6.1/ref/models/fields/#null
    poster_path = models.CharField(max_length=255, blank=True)
    tmdb_id = models.PositiveBigIntegerField(
        unique=True,
        null=True,
        blank=True,
    )


    def __str__(self):
        return self.title

    @property
    def personal_ranking_url(self):
        return reverse("rankings:movie", kwargs={
            "title": self.title,
        })

class MovieGrouping(models.Model):
    """
    Represents a grouping of movies, such as a series or franchise.
    """
    display_name = models.CharField(max_length=200, blank=True)

    movies = models.ManyToManyField(
        Movie,
        related_name="groupings",
    )

    @property
    def display_release_years(self):
        years = sorted(
            movie.release_year
            for movie in self.movies.all()
        )

        if not years:
            return ""

        if len(years) == 1:
            return str(years[0])

        if len(years) == 2:
            return f"{years[0]} & {years[1]}"

        return f"{years[0]}–{years[-1]}"

    def __str__(self):
        if self.display_name:
            return self.display_name

        return ", ".join(str(movie) for movie in self.movies.all())

class MovieTopListEntry(models.Model):
    """
    Represents an entry in a top list, which can be either a single movie or a grouping of movies.
    """
    rank = models.PositiveSmallIntegerField(unique=True)
    notes = models.TextField(blank=True)

    movie = models.OneToOneField(
        Movie,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    grouping = models.OneToOneField(
        MovieGrouping,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["rank"]
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(movie__isnull=False, grouping__isnull=True)
                    | Q(movie__isnull=True, grouping__isnull=False)
                ),
                name="toplist_entry_has_one_entity",
            )
        ]

    def __str__(self):
        entity = self.movie or self.grouping
        return f"#{self.rank} - {entity}"

# ======================================================================================================================

# Album Models
class Album(models.Model):
    """
    Represents a music album in the database.
    """
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    release_year = models.PositiveSmallIntegerField()
    cover_art_path = models.CharField(max_length=255, blank=True)
    musicbrainz_id = models.UUIDField(
        unique=True,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.title} by {self.artist}"

class AlbumTopListEntry(models.Model):
    """
    Represents an entry in a top list for albums.
    """
    rank = models.PositiveSmallIntegerField(unique=True)

    album = models.OneToOneField(
        Album,
        on_delete=models.CASCADE,
        related_name="toplist_entry",
    )

    class Meta:
        ordering = ["rank"]

    def __str__(self):
        return f"#{self.rank} - {self.album}"