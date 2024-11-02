from django.contrib.auth import logout
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
        if hasattr(user, 'club'):
            return redirect('clubs:club_detail', user.club.pk)
        else:
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
    next_page = reverse_lazy('accounts:login')
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)