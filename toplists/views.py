from django.shortcuts import render

from toplists.models import Movie


# Create your views here.
def index(request):
    return render(request, 'toplists/index.html')

def movies(request):
    movies = Movie.objects.all()
    return render(request, 'toplists/movies.html', {'movies': movies})

def albums(request):
    return render(request, 'toplists/albums.html')