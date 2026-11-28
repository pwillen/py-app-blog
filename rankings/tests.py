from django.test import TestCase

from rankings.models import (
    EvaluationCategory,
    MovieCategoryRating,
    MovieEvaluation,
)
from toplists.models import Movie


class MovieEvaluationTests(TestCase):
    def setUp(self):
        """
        Set up the test db with a movie, an evaluation, and all categories.
        Returns:

        """
        self.movie = Movie.objects.create(
            title="Test Movie",
            release_year=2026,
        )

        self.evaluation = MovieEvaluation.objects.create(
            movie=self.movie,
        )

        self.categories = list(EvaluationCategory.objects.all())

    def add_ratings(self, scores: list[int | None]) -> None:
        """
        Helper function to add ratings to a category
        Args:
            scores: list of scores. Does NOT have to be the same length as the number
            of categories, but if it is not, the extra categories will be ignored.

        Returns: None. Creates MovieCategoryRating objects for each category and score.

        """
        for category, score in zip(self.categories, scores):
            MovieCategoryRating.objects.create(
                evaluation=self.evaluation,
                category=category,
                score=score,
            )

    def test_incomplete_evaluation_returns_none(self) -> None:
        """
        Test case with 11 categories rated, but one category is missing.
        The personal_score should return None.

        Returns: None

        """
        self.add_ratings([8] * 11)

        self.assertIsNone(self.evaluation.personal_score)

    def test_unscored_category_returns_no_personal_score(self):
        """
        Test case with 11 categories rated, but one category is unscored (None).
        The personal_score should return None.

        Returns: None

        """
        self.add_ratings([8] * 11 + [None])

        self.assertIsNone(self.evaluation.personal_score)

    def test_complete_evaluation_returns_average(self) -> None:
        """
        Test case with all categories rated.
        The personal_score should return the average of the scores.

        Returns: None

        """
        self.add_ratings(
            [
                10,
                9,
                10,
                9,
                8,
                9,
                9,
                8,
                7,
                6,
                7,
                5,
            ]
        )

        self.assertEqual(self.evaluation.personal_score, 8.1)

    def test_perfect_evaluation_returns_ten(self) -> None:
        """
        Test case with all categories rated as 10.
        The personal_score should return 10.0.

        Returns: None

        """
        self.add_ratings([10] * 12)

        self.assertEqual(self.evaluation.personal_score, 10.0)

    def test_incomplete_evaluation_returns_no_counterbalance(self) -> None:
        """
        Test case with 11 categories rated, but one category is missing.
        The counterbalance_score should return None.

        Returns: None

        """
        self.add_ratings([8] * 11)

        self.assertIsNone(self.evaluation.counterbalance_score)

    def test_unscored_category_returns_no_counterbalance_score(self):
        """
        Test case with 11 categories rated, but one category is unscored (None).
        The counterbalance_score should return None.

        Returns: None

        """
        self.add_ratings([8] * 11 + [None])

        self.assertIsNone(self.evaluation.counterbalance_score)

    def test_lower_importance_categories_receive_greater_adjustment(self):
        """
        Test case with lower importance categories receiving greater adjustments.
        The counterbalance_score should be greater than the personal_score.

        Returns: None

        """
        self.add_ratings(
            [
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                10,
                1,
            ]
        )

        self.assertGreater(
            self.evaluation.counterbalance_score,
            self.evaluation.personal_score,
        )