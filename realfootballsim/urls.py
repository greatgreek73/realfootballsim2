from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from accounts.views import SignUpView

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
]

# API URLs
try:
    urlpatterns += [path('api/', include(('api.urls', 'api'), namespace='api'))]
except Exception:
    pass
