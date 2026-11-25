from django.shortcuts import render

from toplists.models import MovieTopListEntry, AlbumTopListEntry


# Create your views here.
def index(request):
    return render(request, "toplists/index.html")


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