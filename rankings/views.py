from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, 'rankings/index.html')

def movie(request, title):
    return "Movie page for: " + title