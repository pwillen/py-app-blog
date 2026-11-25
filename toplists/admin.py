"""
Django admin for Movie and Album toplists
"""
from urllib.parse import urlencode
from uuid import UUID

import httpx
from django import forms
from django.contrib import admin, messages
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import URLPattern, path, reverse

from toplists.models import (
    Album,
    AlbumTopListEntry,
    Movie,
    MovieGrouping,
    MovieTopListEntry,
)
from toplists.services.tmdb import TMDBClient
from toplists.services.musicbrainz import MusicBrainzClient


# TODO These TMDB form class may get moved to a separate space for usage outside of the
#  admin interface in the future.
class TMDBSearchForm(forms.Form):
    """
    Form for searching movies on TMDB.
    """
    movie_query = forms.CharField(
        max_length=200,
        strip=True,
        widget=forms.SearchInput(attrs={"placeholder": "Search movies..."}),
    )


class TMDBImportForm(forms.Form):
    """
    Form for importing a movie from TMDB.
    """
    tmdb_id = forms.IntegerField(min_value=1)


# Movie Admin
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    """
    Admin interface for the Movie model, including TMDB search and import functionality.
    """

    list_display = ("title", "release_year")
    search_fields = ("title",)
    list_filter = ("release_year",)
    ordering = ("title",)
    change_list_template = "admin/toplists/movie/change_list.html"

    # Append a custom URL for the TMDB search view to the admin URLs
    def get_urls(self) -> list[URLPattern]:
        """
        Returns the custom URLs for the TMDB search and import views.
        Returns: list of URLPattern objects for the admin interface.
        """
        urls = super().get_urls()

        custom_urls = [
            path(
                "tmdb-search/",
                self.admin_site.admin_view(self.tmdb_search_view),
                name="toplists_movie_tmdb_search",
            ),
            path(
                "tmdb-import/",
                self.admin_site.admin_view(self.tmdb_import_view),
                name="toplists_movie_tmdb_import",
            ),
        ]

        return custom_urls + urls

    def tmdb_search_view(self, request: HttpRequest) -> HttpResponse:
        """
        View for searching movies on TMDB and displaying the results in the admin
        interface.
        Args:
            request: The movie query request form from the admin interface.

        Returns: The TMDB search results page

        """
        form = TMDBSearchForm(request.GET or None)
        results = []

        if form.is_valid():
            query = form.cleaned_data["movie_query"]

            try:
                with TMDBClient() as tmdb:
                    response = tmdb.search_movies(query)

                results = response.results

            except httpx.HTTPError as exc:
                messages.error(request, f"TMDB search failed: {exc}")

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Search TMDB",
            "form": form,
            "results": results,
        }

        return render(
            request,
            "admin/toplists/movie/tmdb_search.html",
            context,
        )

    def tmdb_import_view(self, request: HttpRequest) -> HttpResponseRedirect:
        """
        View for importing a movie from TMDB into the local database.
        Args:
            request: The import request form from the admin interface.

        Returns: A redirect to the movie change page or the TMDB search page, depending
        on the outcome of the import.

        """
        form = TMDBImportForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Invalid TMDB ID.")
            return redirect("admin:toplists_movie_tmdb_search")

        tmdb_id = form.cleaned_data["tmdb_id"]

        try:
            with TMDBClient() as tmdb:
                movie_data = tmdb.get_movie(tmdb_id)

            movie_defaults = {
                "tmdb_id": movie_data.id,
                "title": movie_data.title,
                "poster_path": movie_data.poster_path or "",
            }

            if movie_data.release_year is None:
                messages.warning(
                    request,
                    f"{movie_data.title} needs a release year before importing.",
                )

                return redirect(
                    f"{reverse('admin:toplists_movie_add')}?{urlencode(movie_defaults)}"
                )

            movie, created = Movie.objects.update_or_create(
                tmdb_id=movie_data.id,
                defaults={
                    **movie_defaults,
                    "release_year": movie_data.release_year,
                },
            )

            if created:
                messages.success(
                    request,
                    f"{movie.title} imported successfully.",
                )
            else:
                messages.success(
                    request,
                    f"{movie.title} already existed and was updated.",
                )

            return redirect(reverse("admin:toplists_movie_change", args=[movie.pk]))

        except (ValueError, httpx.HTTPError) as exc:
            messages.error(request, f"Import failed: {exc}")
            return redirect("admin:toplists_movie_tmdb_search")


@admin.register(MovieGrouping)
class MovieGroupingAdmin(admin.ModelAdmin):
    """
    Admin interface for the MovieGrouping model, allowing management of movie groupings.
    """

    list_display = ("__str__", "display_release_years")
    search_fields = (
        "display_name",
        "movies__title",
    )
    list_filter = ("movies__release_year",)
    filter_horizontal = ("movies",)


@admin.register(MovieTopListEntry)
class TopListEntryAdmin(admin.ModelAdmin):
    """
    Admin interface for the MovieTopListEntry model, allowing management of top list
    entries.
    """

    list_display = (
        "rank",
        "movie",
        "grouping",
    )
    search_fields = (
        "movie__title",
        "grouping__display_name",
        "grouping__movies__title",
    )
    list_filter = (
        "rank",
        "movie__release_year",
        "grouping__movies__release_year",
    )
    ordering = ("rank",)


# ======================================================================================

class MusicBrainzSearchForm(forms.Form):
    """
    Form for searching albums on MusicBrainz.
    """
    album_query = forms.CharField(
        max_length=200,
        strip=True,
        widget=forms.SearchInput(attrs={"placeholder": "Search albums..."}),)

class MusicBrainzImportForm(forms.Form):
    """
    Form for importing an album from MusicBrainz.
    """
    musicbrainz_id = forms.UUIDField()

# Album Admin
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    """
    Admin interface for the Album model, allowing management of albums.
    """

    list_display = ("__str__", "release_year")
    search_fields = ("title", "artist")
    list_filter = ("release_year",)

    # Append a custom URL for the TMDB search view to the admin URLs
    def get_urls(self) -> list[URLPattern]:
        """
        Returns the custom URLs for the MusicBrainz search and import views.
        Returns: list of URLPattern objects for the admin interface.
        """
        urls = super().get_urls()

        custom_urls = [
            path(
                "musicbrainz-search/",
                self.admin_site.admin_view(self.musicbrainz_search_view),
                name="toplists_album_musicbrainz_search",
            ),
            path(
                "musicbrainz-preview/<uuid:musicbrainz_id>/",
                self.admin_site.admin_view(self.musicbrainz_preview_view),
                name="toplists_album_musicbrainz_preview",
            ),
            path(
                "musicbrainz-import/",
                self.admin_site.admin_view(self.musicbrainz_import_view),
                name="toplists_album_musicbrainz_import",
            ),
        ]

        return custom_urls + urls

    def musicbrainz_search_view(self, request: HttpRequest) -> HttpResponse:
        """
        View for searching albums on MusicBrainz and displaying the results in the admin
        interface.
        Args:
            request: The album query request form from the admin interface.

        Returns: The MusicBrainz search results page

        """
        form = MusicBrainzSearchForm(request.GET or None)
        results = []

        if form.is_valid():
            query = form.cleaned_data["album_query"]

            try:
                with MusicBrainzClient() as musicbrainz:
                    response = musicbrainz.search_release_groups(query)

                results = response.release_groups

            except httpx.HTTPError as exc:
                messages.error(request, f"MusicBrainz search failed: {exc}")

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Search MusicBrainz",
            "form": form,
            "results": results,
        }

        return render(
            request,
            "admin/toplists/album/musicbrainz_search.html",
            context,
        )

    def musicbrainz_preview_view(
            self,
            request: HttpRequest,
            musicbrainz_id: UUID,
    ) -> HttpResponse:
        """
        View for previewing an album from MusicBrainz before importing it.

        Args:
            request: The HTTP request.
            musicbrainz_id: The MusicBrainz release group UUID.

        Returns:
            The album preview page.
        """
        try:
            with MusicBrainzClient() as musicbrainz:
                album_data = musicbrainz.get_release_group(str(musicbrainz_id))
                cover_art_url = musicbrainz.get_cover_art_url(str(musicbrainz_id))

        except httpx.HTTPError as exc:
            messages.error(request, f"Album preview failed: {exc}")
            return redirect("admin:toplists_album_musicbrainz_search")

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": f"Preview {album_data.title}",
            "album": album_data,
            "cover_art_url": cover_art_url,
        }

        return render(
            request,
            "admin/toplists/album/musicbrainz_preview.html",
            context,
        )

    def musicbrainz_import_view(self, request: HttpRequest) -> HttpResponseRedirect:
        """
        View for importing an album from MusicBrainz into the local database.
        Args:
            request: The import request form from the admin interface.

        Returns: A redirect to the album change page or the MusicBrainz search page, depending
        on the outcome of the import.

        """
        form = MusicBrainzImportForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Invalid MusicBrainz ID.")
            return redirect("admin:toplists_album_musicbrainz_search")

        musicbrainz_id = form.cleaned_data["musicbrainz_id"]

        try:
            with MusicBrainzClient() as musicbrainz:
                album_data = musicbrainz.get_release_group(str(musicbrainz_id))
                cover_art_url = musicbrainz.get_cover_art_url(str(musicbrainz_id))

            album_defaults = {
                "title": album_data.title,
                "artist": album_data.artist_name,
                "musicbrainz_id": album_data.id,
                "cover_art_path": cover_art_url or "",
            }

            if album_data.release_year is None:
                messages.warning(
                    request,
                    f"{album_data.title} needs a release year before importing.",
                )

                return redirect(
                    f"{reverse('admin:toplists_album_add')}?{urlencode(album_defaults)}"
                )

            album, created = Album.objects.update_or_create(
                musicbrainz_id=album_data.id,
                defaults={
                    **album_defaults,
                    "release_year": album_data.release_year,
                },
            )

            if created:
                messages.success(
                    request,
                    f"{album.title} imported successfully.",
                )
            else:
                messages.success(
                    request,
                    f"{album.title} already existed and was updated.",
                )

            return redirect(reverse("admin:toplists_album_change", args=[album.pk]))

        except (ValueError, httpx.HTTPError) as exc:
            messages.error(request, f"Import failed: {exc}")
            return redirect("admin:toplists_album_musicbrainz_search")


@admin.register(AlbumTopListEntry)
class AlbumTopListEntryAdmin(admin.ModelAdmin):
    """
    Admin interface for the AlbumTopListEntry model, allowing management of top list
    entries.
    """

    list_display = (
        "rank",
        "album",
    )
    search_fields = ("album__title",)
    list_filter = (
        "rank",
        "album__release_year",
    )
    ordering = ("rank",)