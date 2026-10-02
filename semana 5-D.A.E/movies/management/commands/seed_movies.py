"""Load sample data for the movies catalog."""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction

from movies.models import Genre, Movie, Person, Rating

GENRES = [
    ('Drama', 'Historias reales e imaginadas con fuerte carga emocional.'),
    ('Science Fiction', 'Narrativas con ciencia, tecnologia y futuro.'),
    ('Action', 'Producciones con escenas de accion y ritmo rapido.'),
    ('Comedy', 'Peliculas orientadas al humor y al entretenimiento.'),
]

PEOPLE = [
    ('Denis', 'Villeneuve', date(1967, 10, 3)),
    ('Sofia', 'Coppola', date(1971, 5, 14)),
    ('Alejandro', 'Inarritu', date(1963, 9, 15)),
    ('Greta', 'Gerwig', date(1983, 8, 3)),
    ('Niles', 'Fleckman', date(1977, 3, 27)),
    ('Ana', 'Ruiz', date(1990, 2, 20)),
    ('Luis', 'Torres', date(1988, 11, 8)),
]

MOVIES = [
    {
        'title': 'The Matrix',
        'release_year': 1999,
        'duration_minutes': 136,
        'synopsis': 'Un programador descubre que la realidad es una simulacion.',
        'genres': ['Science Fiction', 'Action'],
        'directors': ['Denis Villeneuve'],
        'actors': ['Ana Ruiz'],
    },
    {
        'title': 'Arrival',
        'release_year': 2016,
        'duration_minutes': 116,
        'synopsis': 'Una linguista intenta comunicarse con visitantes extraterrestres.',
        'genres': ['Science Fiction', 'Drama'],
        'directors': ['Denis Villeneuve'],
        'actors': ['Luis Torres'],
    },
    {
        'title': 'Dune Part Two',
        'release_year': 2024,
        'duration_minutes': 166,
        'synopsis': 'Paul Atreides se une a los Fremen en su guerra contra los Harkonnen.',
        'genres': ['Science Fiction', 'Action'],
        'directors': ['Denis Villeneuve'],
        'actors': ['Ana Ruiz', 'Luis Torres'],
    },
    {
        'title': 'Inception',
        'release_year': 2010,
        'duration_minutes': 148,
        'synopsis': 'Un equipo de ladrones entra en los suenos para robar secretos.',
        'genres': ['Science Fiction', 'Action'],
        'directors': ['Alejandro Inarritu'],
        'actors': ['Luis Torres'],
    },
    {
        'title': 'Lost in Translation',
        'release_year': 2003,
        'duration_minutes': 102,
        'synopsis': 'Dos personas solitarias se conocen en Tokio durante unas vacaciones.',
        'genres': ['Drama', 'Comedy'],
        'directors': ['Sofia Coppola'],
        'actors': ['Ana Ruiz'],
    },
    {
        'title': 'Roma',
        'release_year': 2018,
        'duration_minutes': 135,
        'synopsis': 'La vida de una mujer mexicana a finales de los anos sesenta.',
        'genres': ['Drama'],
        'directors': ['Sofia Coppola'],
        'actors': ['Ana Ruiz'],
    },
    {
        'title': 'Coco',
        'release_year': 2017,
        'duration_minutes': 105,
        'synopsis': 'Un joven musician viaja al mundo de los muertos.',
        'genres': ['Comedy', 'Drama'],
        'directors': ['Greta Gerwig'],
        'actors': ['Ana Ruiz'],
    },
    {
        'title': 'Bardo',
        'release_year': 2022,
        'duration_minutes': 130,
        'synopsis': 'Una leyenda musical recorre Mexico y sus recuerdos.',
        'genres': ['Comedy', 'Drama'],
        'directors': ['Greta Gerwig'],
        'actors': ['Ana Ruiz', 'Luis Torres'],
    },
    {
        'title': 'The Lost City',
        'release_year': 2022,
        'duration_minutes': 112,
        'synopsis': 'Una pareja de arqueologos encuentra un tesoro escondido.',
        'genres': ['Comedy', 'Action'],
        'directors': ['Niles Fleckman'],
        'actors': ['Luis Torres'],
    },
    {
        'title': 'Sicario Dia del Soldado',
        'release_year': 2018,
        'duration_minutes': 122,
        'synopsis': 'Agentes antinarcoticas persiguen a un capo del cartel.',
        'genres': ['Action', 'Drama'],
        'directors': ['Alejandro Inarritu'],
        'actors': ['Luis Torres'],
    },
]

# Ratings: movie title, person full name, score and comment.
RATINGS = [
    ('The Matrix', 'Ana Ruiz', 10, 'Un clasico que sigue vigente.'),
    ('The Matrix', 'Luis Torres', 9, 'Los efectos y la fotografia son excelentes.'),
    ('Arrival', 'Ana Ruiz', 9, 'El lenguaje y el tiempo como tema central.'),
    ('Arrival', 'Luis Torres', 8, 'Estilo muy cuidado, ritmo lento.'),
    ('Dune Part Two', 'Luis Torres', 10, 'Espectacular de principio a fin.'),
    ('Dune Part Two', 'Ana Ruiz', 9, 'Gran fotografia y banda sonora.'),
    ('Inception', 'Luis Torres', 9, 'El primer nivel es el mejor de todos.'),
    ('Inception', 'Ana Ruiz', 8, 'Algo larga, pero muy bien hecha.'),
    ('Lost in Translation', 'Ana Ruiz', 8, 'Delicada y muy humana.'),
    ('Bardo', 'Luis Torres', 7, 'Divertida, aunque irregular.'),
    ('Roma', 'Ana Ruiz', 9, 'Fotografia y silencio al servicio del relato.'),
    ('Coco', 'Ana Ruiz', 9, 'Emotiva, con una banda sonora memorable.'),
    ('The Lost City', 'Luis Torres', 8, 'Aventura comica y ligera.'),
    ('Sicario Dia del Soldado', 'Luis Torres', 8, 'Tension y persecucion.'),
]


class Command(BaseCommand):
    help = 'Loads sample genres, people, movies and ratings for the lab.'

    @transaction.atomic
    def handle(self, *args, **options):
        genres = self._create_genres()
        people = self._create_people()
        movies = self._create_movies(genres, people)
        self._create_ratings(movies, people)

        self.stdout.write(
            self.style.SUCCESS(
                f'Sample data ready -> genres={Genre.objects.count()} '
                f'people={Person.objects.count()} movies={Movie.objects.count()} '
                f'ratings={Rating.objects.count()}',
            )
        )

    def _create_genres(self):
        for name, description in GENRES:
            Genre.objects.update_or_create(
                name=name,
                defaults={'description': description},
            )
        return {genre.name: genre for genre in Genre.objects.all()}

    def _create_people(self):
        for first_name, last_name, birth_date in PEOPLE:
            Person.objects.update_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={'birth_date': birth_date},
            )
        return {
            f'{person.first_name} {person.last_name}': person
            for person in Person.objects.all()
        }

    def _create_movies(self, genres, people):
        for movie_data in MOVIES:
            movie, _ = Movie.objects.update_or_create(
                title=movie_data['title'],
                defaults={
                    'release_year': movie_data['release_year'],
                    'duration_minutes': movie_data['duration_minutes'],
                    'synopsis': movie_data['synopsis'],
                },
            )
            movie.genres.set([genres[name] for name in movie_data['genres']])
            movie.directors.set(
                [people[name] for name in movie_data['directors']],
            )
            movie.actors.set([people[name] for name in movie_data['actors']])
        return {movie.title: movie for movie in Movie.objects.all()}

    def _create_ratings(self, movies, people):
        for title, person_name, score, comment in RATINGS:
            Rating.objects.update_or_create(
                movie=movies[title],
                person=people[person_name],
                defaults={'score': score, 'comment': comment},
            )
