from django.contrib import admin, messages
from django.shortcuts import render
from django.urls import path

from toplists.models import Movie, TopListEntry, MovieGrouping
from toplists.services.tmdb import TMDBClient


# Register your models here.
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_year")
    search_fields = ("title",)
    list_filter = ("release_year",)
    ordering = ("title",)

    # Append a custom URL for the TMDB search view to the admin URLs
    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "tmdb-search/",
                self.admin_site.admin_view(self.tmdb_search_view),
                name="toplists_movie_tmdb_search",
            ),
        ]

        return custom_urls + urls

    def tmdb_search_view(self, request):
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Search TMDB",
        }

        query = request.GET.get("q", "").strip()

        if query:
            try:
                with TMDBClient() as tmdb:
                    results = tmdb.search_movies(query)

                context["results"] = results.results

            except Exception as exc:
                messages.error(request, f"TMDB search failed: {exc}")

        context["query"] = query

        return render(
            request,
            "admin/toplists/movie/tmdb_search.html",
            context,
        )


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