from django.contrib import admin

from toplists.models import Movie


# Register your models here.
@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'notes')
    search_fields = ('title', 'release_year')
    list_filter = ('release_year',)