from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Club


AVAILABLE_COUNTRIES = [
    ('GB', 'Great Britain'),
    ('ES', 'Spain'),
    ('IT', 'Italy'),
    ('DE', 'Germany'),
    ('FR', 'France'),
    ('PT', 'Portugal'),
    ('GR', 'Greece'),
    ('RU', 'Russia'),
    ('AR', 'Argentina'),
    ('BR', 'Brazil'),
]

class ClubForm(forms.ModelForm):
    country = forms.ChoiceField(
        choices=AVAILABLE_COUNTRIES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Club
        fields = ['name', 'country']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter club name'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        self.instance._skip_clean = True
        return cleaned_data

    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        
        if user:
            instance.owner = user
            instance.is_bot = False
        
        if commit and not hasattr(instance, '_skip_save'):
            instance._skip_save = True
            instance.save()
        
        return instance