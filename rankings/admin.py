"""
Django Admin for Rankings
"""

from django.contrib import admin
from django.http.request import HttpRequest

from rankings.models import (
    EvaluationCategory,
    MovieCategoryRating,
    MovieEvaluation,
    MovieWatch,
)


@admin.register(EvaluationCategory)
class EvaluationCategoryAdmin(admin.ModelAdmin):
    """
    Admin for EvaluationCategory
    """

    list_display = ("name", "importance", "sort_order")
    ordering = ("sort_order",)


class MovieCategoryRatingInline(admin.TabularInline):
    """
    Inline admin for MovieCategoryRating
    """

    model = MovieCategoryRating
    extra = 0

    readonly_fields = ("category_description",)

    fields = ("category", "category_description", "score")

    @admin.display(description="Description")
    def category_description(self, obj):
        """Display the category description."""
        return obj.category.description


@admin.register(MovieEvaluation)
class MovieEvaluationAdmin(admin.ModelAdmin):
    """
    Admin for MovieEvaluation
    """

    list_display = ("movie", "personal_score", "counterbalance_score")
    ordering = ("movie",)

    inlines = [MovieCategoryRatingInline]

    def save_related(self, request: HttpRequest, form, formsets, change) -> None:
        """
        Save related objects and create missing category ratings.

        Args:
            request: The HTTP request object.
            form: The form instance.
            formsets: The formsets for related objects.
            change: A boolean indicating if this is a change or a new object.

        Returns: None. Creates missing MovieCategoryRating objects
        for any categories not already rated.

        """
        super().save_related(request, form, formsets, change)

        evaluation = form.instance

        existing_categories = evaluation.category_ratings.values_list(
            "category_id",
            flat=True,
        )

        missing_categories = EvaluationCategory.objects.exclude(
            id__in=existing_categories,
        )

        MovieCategoryRating.objects.bulk_create(
            [
                MovieCategoryRating(
                    evaluation=evaluation,
                    category=category,
                )
                for category in missing_categories
            ]
        )


@admin.register(MovieWatch)
class MovieWatchAdmin(admin.ModelAdmin):
    """
    Admin for MovieWatch
    """

    list_display = ("movie", "watched_date", "is_rewatch")
    ordering = ("watched_date", "movie")