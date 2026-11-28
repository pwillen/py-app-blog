"""
Django models for the Rankings app
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q

from toplists.models import Movie

EXPECTED_CATEGORY_COUNT = 12


class EvaluationCategory(models.Model):
    """
    Defines a category used to evaluate movies.
    """

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    importance = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ]
    )

    sort_order = models.PositiveSmallIntegerField(unique=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class MovieWatch(models.Model):
    """
    Represents an individual viewing of a movie.
    """

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name="watches",
    )

    watched_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_rewatch = models.BooleanField(default=False)

    class Meta:
        ordering = [
            models.F("watched_date").desc(nulls_last=True),
        ]

    def __str__(self):
        date = self.watched_date or "Unknown date"
        return f"{self.movie} - {date}"


class MovieEvaluation(models.Model):
    """
    Represents an evaluation of a movie.
    """

    movie = models.OneToOneField(
        Movie,
        on_delete=models.CASCADE,
        related_name="evaluation",
    )

    evaluated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Evaluation of {self.movie}"

    @property
    def personal_score(self):
        ratings = self.category_ratings.all()

        if ratings.count() != EXPECTED_CATEGORY_COUNT:
            return None

        if ratings.filter(score__isnull=True).exists():
            return None

        average = ratings.aggregate(average=models.Avg("score"))["average"]

        return round(average, 1)

    @property
    def counterbalance_score(self):
        ratings = self.category_ratings.select_related("category")

        if ratings.count() != EXPECTED_CATEGORY_COUNT:
            return None

        if ratings.filter(score__isnull=True).exists():
            return None

        adjusted_total = 0

        for rating in ratings:
            adjustment = ((10 - rating.category.importance) / 10) * (10 - rating.score)

            adjusted_score = rating.score + adjustment
            adjusted_total += adjusted_score

        return round(adjusted_total / EXPECTED_CATEGORY_COUNT, 1)


class MovieCategoryRating(models.Model):
    """
    Represents a rating for one category within a movie evaluation.
    """

    evaluation = models.ForeignKey(
        MovieEvaluation,
        on_delete=models.CASCADE,
        related_name="category_ratings",
    )

    category = models.ForeignKey(
        EvaluationCategory,
        on_delete=models.PROTECT,
        related_name="ratings",
    )

    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10),
        ],
        null = True,
        blank = True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["evaluation", "category"],
                name="unique_movie_category_rating",
            ),
            models.CheckConstraint(
                condition=Q(score__gte=1) & Q(score__lte=10),
                name="movie_category_score_range",
            ),
        ]

    def __str__(self):
        return f"{self.evaluation.movie} - {self.category}: {self.score}/10"