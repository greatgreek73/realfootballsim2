from django.conf import settings

def timezone_context(request):
    return {
        'TOURNAMENT_TIMEZONES': settings.TOURNAMENT_TIMEZONES,
        'user_timezone': request.session.get('django_timezone', 'UTC')
    }