"""Views for the movies app."""

from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, render

from .models import Genre, Movie

TOP_MOVIES_PER_GENRE = 3


def recommendations(request):
    """
    Public view with the best rated movies grouped by genre.

    Every genre shows its top rated movies, computed from the average of the
    ratings registered in the admin site.
    """
    genres = (
        Genre.objects.annotate(movie_total=Count('movies', distinct=True))
        .filter(movie_total__gt=0)
        .order_by('name')
    )

    top_movies_per_genre = []
    for genre in genres:
        top_movies = (
            Movie.objects.filter(genres=genre, ratings__isnull=False)
            .annotate(average_score=Avg('ratings__score'))
            .order_by('-average_score', 'title')[:TOP_MOVIES_PER_GENRE]
        )
        if top_movies:
            top_movies_per_genre.append(
                {'genre': genre, 'movies': list(top_movies)},
            )

    return render(
        request,
        'movies/recommendations.html',
        {
            'groups': top_movies_per_genre,
            'top_movies_per_genre': TOP_MOVIES_PER_GENRE,
        },
    )


def movie_detail(request, pk):
    """Public page with the details and the ratings of a single movie."""
    movie = get_object_or_404(
        Movie.objects.prefetch_related('genres', 'directors', 'actors'),
        pk=pk,
    )
    ratings = list(movie.ratings.select_related('person').order_by('-score'))

    return render(
        request,
        'movies/movie_detail.html',
        {
            'movie': movie,
            'ratings': ratings,
            'average_rating': movie.average_rating,
            'has_ratings': bool(ratings),
        },
    )


def movie_search(request):
    """Public search of movies by title, year or genre."""
    query = request.GET.get('q', '').strip()

    movies = Movie.objects.prefetch_related('genres')
    if query:
        movies = movies.filter(
            Q(title__icontains=query)
            | Q(release_year__icontains=query)
            | Q(genres__name__icontains=query),
        ).distinct()
    else:
        movies = Movie.objects.none()

    movies = movies.order_by('-release_year', 'title')[:50]

    return render(
        request,
        'movies/movie_search.html',
        {
            'query': query,
            'movies': movies,
            'result_count': len(movies),
        },
    )
