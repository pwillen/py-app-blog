from django.db import models

# Create your models here.
class Movie(models.Model):
    title = models.CharField(max_length=200)
    release_year = models.IntegerField()
    # https://docs.djangoproject.com/en/6.1/ref/models/fields/#null
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title