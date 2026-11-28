"""

"""
from django.shortcuts import render, get_object_or_404

from toplists.models import Movie

def index(request):
    movies = (
        Movie.objects
        .filter(watches__isnull=False)
        .distinct()
        .order_by("title", "release_year")
    )

    return render(
        request,
        "rankings/index.html",
        {"movies": movies},
    )


def movie(request, pk):
    movie = get_object_or_404(Movie, pk=pk)

    watches = movie.watches.all()

    return render(
        request,
        "rankings/movie.html",
        {
            "movie": movie,
            "watches": watches,
        },
    )