"""Database models for the movies app."""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Genre(models.Model):
    """A movie genre such as drama or science fiction."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.name


class Person(models.Model):
    """A person involved in a movie, such as a director or an actor."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField(null=True, blank=True)
    biography = models.TextField(blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = 'Person'
        verbose_name_plural = 'People'

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()


class Movie(models.Model):
    """A movie that can be linked to genres, people and ratings."""

    title = models.CharField(max_length=200, unique=True)
    synopsis = models.TextField(blank=True)
    release_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1888)],
    )
    duration_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
    )
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='movies', blank=True)
    directors = models.ManyToManyField(
        Person,
        related_name='directed_movies',
        blank=True,
    )
    actors = models.ManyToManyField(Person, related_name='acted_movies', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_year', 'title']
        verbose_name = 'Movie'
        verbose_name_plural = 'Movies'
        indexes = [models.Index(fields=['title'])]

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        """Return the mean of the movie ratings, or None when unrated."""
        ratings = [rating.score for rating in self.ratings.all()]
        if not ratings:
            return None
        return round(sum(ratings) / len(ratings), 2)


class Rating(models.Model):
    """A score given by a person to a movie."""

    SCORE_MIN = 1
    SCORE_MAX = 10

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(SCORE_MIN), MaxValueValidator(SCORE_MAX)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score', 'id']
        verbose_name = 'Rating'
        verbose_name_plural = 'Ratings'
        constraints = [
            models.UniqueConstraint(
                fields=['movie', 'person'],
                name='unique_rating_per_movie_and_person',
            ),
        ]

    def __str__(self):
        return f'{self.movie} - {self.score}/10'
