from django.http import HttpResponse


def home(request):
    """Temporary entry point used until the recommendation view is built."""
    return HttpResponse('Movies lab project')
