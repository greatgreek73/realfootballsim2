from django.contrib import admin
from django.urls import path, include, re_path
from matches import views_markov_demo
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from accounts.views import SignUpView
from players.api_views import (
    player_detail_api,
    player_generate_avatar_api,
    player_extra_training_api,
)
from matches.api_views import (
    match_list_api,
    match_detail_api,
    match_events_api,
    match_create_api,
    match_simulate_api,
    match_substitute_api,
)



urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Core app URLs (includes home pages)
    path('', include(('core.urls', 'core'), namespace='core')),
    
    # Authentication URLs with Gogo template style paths
    path('auth/sign-in/', auth_views.LoginView.as_view(
        template_name='auth/sign-in.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    path('auth/sign-out/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Signup view
    path('auth/sign-up/', SignUpView.as_view(), name='signup'),
    
    # Password reset chain
    path('auth/password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password-reset.html',
        email_template_name='registration/password_reset_email.html',
        success_url='/auth/password-reset/done/'
    ), name='password_reset'),
    
    path('auth/password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password-reset-done.html'
    ), name='password_reset_done'),
    
    path('auth/password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password-reset-confirm.html',
        success_url='/auth/password-reset/complete/'
    ), name='password_reset_confirm'),
    
    path('auth/password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password-reset-complete.html'
    ), name='password_reset_complete'),
    
    # Other app URLs
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('clubs/', include(('clubs.urls', 'clubs'), namespace='clubs')),
    path('players/', include(('players.urls', 'players'), namespace='players')),
    path('matches/', include(('matches.urls', 'matches'), namespace='matches')),
    path('tournaments/', include(('tournaments.urls', 'tournaments'), namespace='tournaments')),
    path('transfers/', include(('transfers.urls', 'transfers'), namespace='transfers')),
    path('narrative/', include(('narrative.urls', 'narrative'), namespace='narrative')),
    path("api/auth/", include(("accounts.api_urls", "api-auth"), namespace="api-auth")),
    path("api/transfers/", include(("transfers.api_urls", "transfers_api"), namespace="transfers_api")),
    path("api/", include("clubs.api_urls")),  # API клуба
    path("api/players/<int:pk>/", player_detail_api, name="api_player_detail"),
    path("api/players/<int:pk>/avatar/", player_generate_avatar_api, name="api_player_generate_avatar"),
    path("api/players/<int:pk>/extra-training/", player_extra_training_api, name="api_player_extra_training"),
    path("api/matches/", match_list_api, name="api_matches_list"),
    path("markov-demo/", views_markov_demo.markov_demo, name="markov_demo"),
    path("api/matches/create/", match_create_api, name="api_match_create"),
    path("api/matches/<int:pk>/", match_detail_api, name="api_match_detail"),
    path("api/matches/<int:pk>/events/", match_events_api, name="api_match_events"),
    path("api/matches/<int:pk>/simulate/", match_simulate_api, name="api_match_simulate"),
    path("api/matches/<int:pk>/substitute/", match_substitute_api, name="api_match_substitute"),
]


# API URLs
try:
    urlpatterns += [path('api/', include(('api.urls', 'api'), namespace='api'))]
except Exception:
    pass
