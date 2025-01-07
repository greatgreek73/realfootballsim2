from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth.views import LogoutView as BaseLogoutView
from .forms import CustomUserCreationForm, CustomAuthenticationForm

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        if hasattr(user, 'club'):
            return redirect('clubs:club_detail', user.club.pk)
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

class LogoutView(BaseLogoutView):
    http_method_names = ['get', 'post']
    next_page = reverse_lazy('accounts:login')

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)