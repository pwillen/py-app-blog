from django.shortcuts import render

from toplists.models import AlbumTopListEntry, MovieTopListEntry


# Create your views here.
def index(request):
    movie_entries = (
        MovieTopListEntry.objects
        .filter(grouping__isnull=True)
        .select_related("movie")
        .order_by("rank")[:7]
    )

    album_entries = (
        AlbumTopListEntry.objects
        .select_related("album")
        .order_by("rank")[:7]
    )

    return render(
        request,
        "toplists/index.html",
        {
            "movie_entries": movie_entries,
            "album_entries": album_entries,
        },
    )


def movies(request):
    entries = MovieTopListEntry.objects.select_related(
        "movie",
        "grouping",
    ).prefetch_related(
        "grouping__movies",
    )

    return render(
        request,
        "toplists/movies.html",
        {"entries": entries},
    )


def albums(request):
    entries = AlbumTopListEntry.objects.select_related("album")

    return render(
        request,
        "toplists/albums.html",
        {"entries": entries},
    )