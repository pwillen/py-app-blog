from django.contrib import admin

from toplists.models import Movie, TopListEntry, MovieGrouping


# Register your models here.
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_year")
    search_fields = ("title",)
    list_filter = ("release_year",)
    ordering = ("title",)


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