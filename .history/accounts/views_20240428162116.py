from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from clubs.models import Club

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')  # Перенаправление после регистрации, если специальное перенаправление не активировано

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        if hasattr(user, 'club'):
            # Перенаправление на страницу деталей клуба
            return redirect('clubs:club_detail', user.club.pk)  # Убрано 'kwargs', исправлено на правильный синтаксис
        else:
            # Перенаправление на страницу создания клуба
            return redirect('clubs:create_club')

class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('login')  # Перенаправление после входа, если специальное перенаправление не активировано

    def form_valid(self, form):
        login(self.request, form.get_user())
        user = form.get_user()
        if hasattr(user, 'club'):
            # Перенаправление на страницу деталей клуба
            return redirect('clubs:club_detail', user.club.pk)  # Убрано 'kwargs', исправлено на правильный синтаксис
        else:
            # Перенаправление на страницу создания клуба
            return redirect('clubs:create_club')

class LogoutView(FormView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')  # Перенаправление на страницу входа после выхода из системы
