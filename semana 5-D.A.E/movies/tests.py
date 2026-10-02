"""Tests for the movies app."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Genre, Movie, Person, Rating


class MovieModelTests(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name='Science Fiction')
        self.person = Person.objects.create(
            first_name='Ana',
            last_name='Ruiz',
        )
        self.movie = Movie.objects.create(
            title='The Matrix',
            release_year=1999,
        )
        self.movie.genres.add(self.genre)

    def test_str_returns_the_title(self):
        self.assertEqual(str(self.movie), 'The Matrix')

    def test_average_rating_is_none_without_ratings(self):
        self.assertIsNone(self.movie.average_rating)

    def test_average_rating_is_the_mean_of_the_scores(self):
        Rating.objects.create(movie=self.movie, person=self.person, score=10)
        Rating.objects.create(
            movie=self.movie,
            person=Person.objects.create(first_name='Luis', last_name='Torres'),
            score=8,
        )
        self.assertEqual(self.movie.average_rating, 9)

    def test_score_out_of_range_is_rejected(self):
        rating = Rating(movie=self.movie, person=self.person, score=11)
        with self.assertRaises(ValidationError):
            rating.full_clean()


class RatingConstraintTests(TestCase):
    def test_duplicate_rating_for_same_movie_and_person_is_rejected(self):
        movie = Movie.objects.create(title='Arrival', release_year=2016)
        person = Person.objects.create(first_name='Luis', last_name='Torres')
        Rating.objects.create(movie=movie, person=person, score=8)

        with self.assertRaises(Exception):
            Rating.objects.create(movie=movie, person=person, score=9)


class AdminConfigurationTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username='root',
            email='root@dae.local',
            password='Root12345',
        )
        self.client.force_login(self.admin_user)

    def test_all_four_models_are_registered(self):
        for model in (Movie, Genre, Person, Rating):
            self.assertIn(model, admin.site._registry)

    def test_movie_admin_options(self):
        movie_admin = admin.site._registry[Movie]
        self.assertIn('title', movie_admin.list_display)
        self.assertIn('genres', movie_admin.list_filter)
        self.assertIn('release_year', movie_admin.list_filter)
        self.assertIn('title', movie_admin.search_fields)

    def test_movie_admin_uses_rating_inline_and_readonly_fields(self):
        movie_admin = admin.site._registry[Movie]
        self.assertTrue(movie_admin.inlines)
        self.assertEqual(
            set(movie_admin.readonly_fields),
            {'created_at', 'updated_at'},
        )

    def test_superuser_can_open_the_movie_changelist(self):
        response = self.client.get(reverse('admin:movies_movie_changelist'))
        self.assertEqual(response.status_code, 200)

    def test_movie_form_renders_the_rating_inline(self):
        movie = Movie.objects.create(title='Arrival', release_year=2016)
        response = self.client.get(
            reverse('admin:movies_movie_change', args=[movie.pk]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ratings-0-person')


class RecommendationViewTests(TestCase):
    def setUp(self):
        self.sci_fi = Genre.objects.create(name='Science Fiction')
        self.drama = Genre.objects.create(name='Drama')
        self.person = Person.objects.create(first_name='Ana', last_name='Ruiz')

        self.matrix = Movie.objects.create(
            title='The Matrix',
            release_year=1999,
        )
        self.matrix.genres.add(self.sci_fi)

        self.arrival = Movie.objects.create(
            title='Arrival',
            release_year=2016,
        )
        self.arrival.genres.add(self.sci_fi)

        self.roma = Movie.objects.create(title='Roma', release_year=2018)
        self.roma.genres.add(self.drama)

        other_person = Person.objects.create(first_name='Luis', last_name='Torres')

        Rating.objects.create(
            movie=self.matrix,
            person=self.person,
            score=10,
        )
        Rating.objects.create(movie=self.matrix, person=other_person, score=8)
        Rating.objects.create(movie=self.arrival, person=other_person, score=6)

    def test_view_returns_200(self):
        response = self.client.get(reverse('movies:recommendations'))
        self.assertEqual(response.status_code, 200)

    def test_movies_are_ordered_by_average_score(self):
        response = self.client.get(reverse('movies:recommendations'))
        group = response.context['groups'][0]
        titles = [movie.title for movie in group['movies']]
        self.assertEqual(titles, ['The Matrix', 'Arrival'])

    def test_genre_without_ratings_is_not_listed(self):
        response = self.client.get(reverse('movies:recommendations'))
        listed_genres = [group['genre'].name for group in response.context['groups']]
        self.assertNotIn('Drama', listed_genres)

    def test_movie_detail_returns_200(self):
        response = self.client.get(
            reverse('movies:movie_detail', args=[self.matrix.pk]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['movie'], self.matrix)
        self.assertEqual(response.context['average_rating'], 9)

    def test_movie_detail_returns_404_for_missing_movie(self):
        response = self.client.get(reverse('movies:movie_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_search_filters_by_title(self):
        response = self.client.get(
            reverse('movies:movie_search'),
            {'q': 'Matrix'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [movie.title for movie in response.context['movies']],
            ['The Matrix'],
        )

    def test_search_filters_by_genre(self):
        response = self.client.get(
            reverse('movies:movie_search'),
            {'q': 'Science Fiction'},
        )
        self.assertEqual(len(response.context['movies']), 2)

    def test_search_without_query_returns_no_results(self):
        response = self.client.get(reverse('movies:movie_search'))
        self.assertEqual(list(response.context['movies']), [])


class EditorPermissionsTests(TestCase):
    def setUp(self):
        call_command('setup_editor_permissions')

    def test_group_has_add_and_change_but_not_delete(self):
        group = Group.objects.get(name='editores')
        codenames = set(group.permissions.values_list('codename', flat=True))
        self.assertIn('add_movie', codenames)
        self.assertIn('change_movie', codenames)
        self.assertNotIn('delete_movie', codenames)

    def test_editor_can_open_the_movie_add_page(self):
        self.client.login(username='editor', password='Editor12345')
        response = self.client.get(reverse('admin:movies_movie_add'))
        self.assertEqual(response.status_code, 200)

    def test_editor_cannot_open_the_movie_delete_page(self):
        self.client.login(username='editor', password='Editor12345')
        movie = Movie.objects.create(title='Arrival', release_year=2016)
        response = self.client.get(
            reverse('admin:movies_movie_delete', args=[movie.pk]),
        )
        self.assertEqual(response.status_code, 403)

    def test_editor_does_not_see_other_models(self):
        self.client.login(username='editor', password='Editor12345')
        response = self.client.get(reverse('admin:index'))
        self.assertNotContains(response, reverse('admin:movies_person_changelist'))

    def test_setup_command_is_idempotent(self):
        call_command('setup_editor_permissions')
        self.assertEqual(Group.objects.filter(name='editores').count(), 1)
        codenames = set(
            Group.objects.get(name='editores')
            .permissions.values_list('codename', flat=True),
        )
        self.assertEqual(codenames, {'add_movie', 'change_movie'})


class SeedCommandTests(TestCase):
    def test_seed_creates_ten_movies_four_genres_and_ratings(self):
        call_command('seed_movies')
        self.assertEqual(Genre.objects.count(), 4)
        self.assertEqual(Movie.objects.count(), 10)
        self.assertGreaterEqual(
            Movie.objects.filter(ratings__isnull=False).distinct().count(),
            5,
        )

    def test_seed_is_idempotent(self):
        call_command('seed_movies')
        call_command('seed_movies')
        self.assertEqual(Movie.objects.count(), 10)
        self.assertEqual(Genre.objects.count(), 4)
