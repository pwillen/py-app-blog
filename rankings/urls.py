from django.urls import path

from rankings import views

app_name = "rankings"
urlpatterns = [
    path("", views.index, name="index"),
    path("movies/<str:title>/", views.movie, name="movie"),
]
