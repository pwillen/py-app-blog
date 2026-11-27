from django.shortcuts import render


def index(request):
    return render(request, "home/index.html")


def acknowledgements(request):
    return render(request, "home/acknowledgements.html")
