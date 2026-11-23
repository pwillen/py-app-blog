import httpx
from django.contrib import admin, messages
from django import forms
from django.shortcuts import render, redirect
from django.urls import path, reverse

from toplists.models import Movie, TopListEntry, MovieGrouping
from toplists.services.tmdb import TMDBClient

# TODO These TMDB form class may get moved to a separate space for usage outside of the admin interface in the future.
class TMDBSearchForm(forms.Form):
    movie_query = forms.CharField(
        max_length=200,
        strip=True,
        widget=forms.SearchInput(
            attrs={"placeholder": "Search movies..."}
        ),
    )

class TMDBImportForm(forms.Form):
    tmdb_id = forms.IntegerField(min_value=1)

# Register your models here.
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_year")
    search_fields = ("title",)
    list_filter = ("release_year",)
    ordering = ("title",)
    change_list_template = "admin/toplists/movie/change_list.html"

    # Append a custom URL for the TMDB search view to the admin URLs
    def get_urls(self):
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

    def tmdb_search_view(self, request):
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

    def tmdb_import_view(self, request):
        form = TMDBImportForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Invalid TMDB ID.")
            return redirect("admin:toplists_movie_tmdb_search")

        tmdb_id = form.cleaned_data["tmdb_id"]

        try:
            with TMDBClient() as tmdb:
                movie_data = tmdb.get_movie(tmdb_id)

            if movie_data.release_year is None:
                messages.warning(
                    request,
                    f"{movie_data.title} needs a release year before importing.",
                )

                return redirect(
                    reverse("admin:toplists_movie_add")
                    + f"?tmdb_id={movie_data.id}"
                    + f"&title={movie_data.title}"
                    + f"&poster_path={movie_data.poster_path or ''}"
                )

            movie, created = Movie.objects.update_or_create(
                tmdb_id=movie_data.id,
                defaults={
                    "title": movie_data.title,
                    "release_year": movie_data.release_year,
                    "poster_path": movie_data.poster_path or "",
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

            return redirect(
                reverse("admin:toplists_movie_change", args=[movie.pk])
            )

        except (ValueError, httpx.HTTPError) as exc:
            messages.error(request, f"Import failed: {exc}")
            return redirect("admin:toplists_movie_tmdb_search")



@admin.register(MovieGrouping)
class MovieGroupingAdmin(admin.ModelAdmin):
    list_display = ("__str__", "display_release_years")
    search_fields = (
        "display_name",
        "movies__title",
    )
    list_filter = ("movies__release_year",)
    filter_horizontal = ("movies",)


@admin.register(TopListEntry)
class TopListEntryAdmin(admin.ModelAdmin):
    list_display = ("rank", "movie", "grouping",)
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