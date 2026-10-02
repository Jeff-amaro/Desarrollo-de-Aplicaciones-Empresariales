"""Admin configuration for the movies app."""

from django.contrib import admin

from .models import Genre, Movie, Person, Rating


class RatingInline(admin.TabularInline):
    """Ratings shown as a block of rows inside the movie form."""

    model = Rating
    extra = 1
    fields = ('person', 'score', 'comment')
    autocomplete_fields = ('person',)
    verbose_name = 'Rating'
    verbose_name_plural = 'Ratings'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'movie_count')
    search_fields = ('name',)
    ordering = ('name',)

    @admin.display(description='Movies')
    def movie_count(self, obj):
        return obj.movies.count()


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'birth_date')
    search_fields = ('first_name', 'last_name')
    list_filter = ('birth_date',)
    ordering = ('last_name', 'first_name')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'genre_list', 'average_rating')
    list_filter = ('genres', 'release_year')
    search_fields = ('title', 'synopsis')
    ordering = ('-release_year', 'title')
    filter_horizontal = ('genres', 'directors', 'actors')
    inlines = (RatingInline,)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'synopsis', 'poster')}),
        ('Details', {'fields': ('release_year', 'duration_minutes')}),
        ('Classification', {'fields': ('genres',)}),
        ('People', {'fields': ('directors', 'actors')}),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'description': 'These fields are filled automatically and cannot be edited.',
        }),
    )

    @admin.display(description='Genres')
    def genre_list(self, obj):
        return ', '.join(genre.name for genre in obj.genres.all())

    @admin.display(description='Average rating')
    def average_rating(self, obj):
        return obj.average_rating or '-'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('movie', 'person', 'score')
    list_filter = ('score',)
    search_fields = ('movie__title', 'person__first_name', 'person__last_name')
    ordering = ('-score',)
    autocomplete_fields = ('person',)
