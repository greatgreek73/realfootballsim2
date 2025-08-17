from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
import json

# SignUpView using UserCreationForm with CustomUser model
class SignUpView(CreateView):
    model = get_user_model()
    form_class = UserCreationForm
    template_name = 'auth/sign-up.html'
    success_url = reverse_lazy('core:home')
    
    def get_form_class(self):
        """Override to ensure UserCreationForm uses our custom user model"""
        from django import forms
        
        class CustomModelUserCreationForm(UserCreationForm):
            class Meta:
                model = get_user_model()
                fields = ("username",)
                
        return CustomModelUserCreationForm
    
    def form_valid(self, form):
        """Log in the user after successful registration"""
        self.object = form.save()
        login(self.request, self.object)
        return redirect(self.get_success_url())
    
    def form_invalid(self, form):
        """Debug: print form errors to console"""
        print("Form errors:", form.errors.as_json())
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:home')
        return super().get(request, *args, **kwargs)