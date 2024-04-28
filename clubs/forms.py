# clubs/forms.py
from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Club

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'country']
        widgets = {
            'country': CountrySelectWidget()  # Использует виджет выбора страны, предоставляемый django-countries
        }
