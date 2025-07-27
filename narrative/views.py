from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import timedelta

# Import models from matches app
from matches.models import NarrativeEvent, Match
from clubs.models import Club


class StoryCenterView(LoginRequiredMixin, TemplateView):
    """Main view for the Story Center Dashboard."""
    template_name = 'narrative/story_center.html'
    
    def get(self, request, *args, **kwargs):
        """Handle both regular and AJAX requests."""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_ajax_request(request)
        return super().get(request, *args, **kwargs)
    
    def handle_ajax_request(self, request):
        """Handle AJAX request for loading more stories."""
        offset = int(request.GET.get('offset', 0))
        limit = 50
        
        # Get filter parameters
        club_filter = request.GET.get('club')
        event_type_filter = request.GET.get('event_type')
        importance_filter = request.GET.get('importance')
        time_period = request.GET.get('time_period', 'all')
        
        # Build queryset
        narratives = self.get_filtered_narratives(
            club_filter, event_type_filter, importance_filter, time_period
        )
        
        # Get paginated results
        stories = narratives[offset:offset + limit]
        has_more = narratives.count() > offset + limit
        
        # Render stories as HTML
        html = render_to_string('narrative/partials/story_cards.html', {
            'stories': stories,
        })
        
        return JsonResponse({
            'html': html,
            'has_more': has_more,
        })
    
    def get_filtered_narratives(self, club_filter, event_type_filter, importance_filter, time_period):
        """Get filtered narrative events queryset."""
        narratives = NarrativeEvent.objects.select_related(
            'primary_player',
            'secondary_player',
            'match',
            'match__home_club',
            'match__away_club'
        ).order_by('-timestamp')
        
        # Apply time period filter
        if time_period == '7days':
            date_threshold = timezone.now() - timedelta(days=7)
            narratives = narratives.filter(timestamp__gte=date_threshold)
        elif time_period == '30days':
            date_threshold = timezone.now() - timedelta(days=30)
            narratives = narratives.filter(timestamp__gte=date_threshold)
        
        # Apply club filter
        if club_filter:
            narratives = narratives.filter(
                Q(primary_player__club_id=club_filter) |
                Q(secondary_player__club_id=club_filter) |
                Q(match__home_club_id=club_filter) |
                Q(match__away_club_id=club_filter)
            )
        
        # Apply event type filter
        if event_type_filter:
            narratives = narratives.filter(event_type=event_type_filter)
        
        # Apply importance filter
        if importance_filter:
            narratives = narratives.filter(importance=importance_filter)
        
        return narratives
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if personality engine is enabled
        use_personality_engine = getattr(settings, 'USE_PERSONALITY_ENGINE', True)
        
        if use_personality_engine:
            # Get filter parameters from request
            club_filter = self.request.GET.get('club')
            event_type_filter = self.request.GET.get('event_type')
            importance_filter = self.request.GET.get('importance')
            time_period = self.request.GET.get('time_period', 'all')
            
            # Get filtered narratives
            narratives = self.get_filtered_narratives(
                club_filter, event_type_filter, importance_filter, time_period
            )
            
            # Get important stories (major or legendary)
            important_narratives = narratives.filter(
                importance__in=['major', 'legendary']
            )[:10]
            
            # Get all narratives (paginated in template)
            all_narratives = narratives[:50]  # Initial load limit
            
            # Get filter data
            all_clubs = Club.objects.all().order_by('name')
            event_types = NarrativeEvent.EVENT_TYPES
            importance_levels = NarrativeEvent.IMPORTANCE_LEVELS
            
            context.update({
                'page_title': 'Story Center',
                'active_page': 'story_center',
                'use_personality_engine': use_personality_engine,
                'important_stories': important_narratives,
                'all_stories': all_narratives,
                'clubs': all_clubs,
                'event_types': event_types,
                'importance_levels': importance_levels,
                'current_filters': {
                    'club': club_filter,
                    'event_type': event_type_filter,
                    'importance': importance_filter,
                    'time_period': time_period,
                },
                'total_stories': narratives.count(),
            })
        else:
            # Personality engine disabled
            context.update({
                'page_title': 'Story Center',
                'active_page': 'story_center',
                'use_personality_engine': use_personality_engine,
                'important_stories': [],
                'all_stories': [],
                'clubs': [],
                'event_types': [],
                'importance_levels': [],
                'current_filters': {},
                'total_stories': 0,
            })
        
        return context