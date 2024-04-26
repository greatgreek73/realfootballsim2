from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth import login, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('index')  # Укажите URL, куда перенаправлять после успешной регистрации

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy('index')  # Укажите URL, куда перенаправлять после успешного входа

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

class LogoutView(FormView):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('login')  # Укажите URL, куда перенаправлять после выхода
