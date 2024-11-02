from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LogoutView as AuthLogoutView
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from clubs.models import Club

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')  # Добавлен namespace

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        if hasattr(user, 'club'):
            # Redirect to club details page
            return redirect('clubs:club_detail', user.club.pk)
        else:
            # Redirect to club creation page
            return redirect('clubs:create_club')

class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    
    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        
        if hasattr(user, 'club'):
            return redirect('clubs:club_detail', user.club.pk)
        return redirect('clubs:create_club')

class LogoutView(AuthLogoutView):
    next_page = reverse_lazy('accounts:login')  # Добавлен namespace
    
    def dispatch(self, request, *args, **kwargs):
        # Дополнительная логика при выходе, если потребуется
        response = super().dispatch(request, *args, **kwargs)
        return response