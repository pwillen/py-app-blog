from django.urls import path

from toplists import views

app_name = "toplists"
urlpatterns = [
    path("", views.index, name="index"),
    path("movies/", views.movies, name="movies"),
    path("albums/", views.albums, name="albums")
]