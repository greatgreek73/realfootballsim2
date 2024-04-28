from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from clubs.models import Club

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    # Меняем success_url, так как теперь он будет определен в методе form_valid
    success_url = reverse_lazy('login')  # Будет использоваться, если не переопределить в form_valid

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        # Проверяем, существует ли клуб для пользователя
        if hasattr(user, 'club'):
            return redirect('club_detail')  # Используем имя URL из вашего приложения clubs
        else:
            return redirect('create_club')  # Имя URL для страницы создания клуба

class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    # Меняем success_url, так как теперь он будет определен в методе form_valid
    success_url = reverse_lazy('login')  # Будет использоваться, если не переопределить в form_valid

    def form_valid(self, form):
        login(self.request, form.get_user())
        user = form.get_user()
        # Проверяем, существует ли клуб для пользователя
        if hasattr(user, 'club'):
            return redirect('club_detail')  # Используем имя URL из вашего приложения clubs
        else:
            return redirect('create_club')  # Имя URL для страницы создания клуба

class LogoutView(FormView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')  # Перенаправление на страницу входа после выхода из системы
