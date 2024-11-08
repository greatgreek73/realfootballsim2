from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Club

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['name', 'country']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter club name'
            }),
            'country': CountrySelectWidget(attrs={
                'class': 'form-control'
            })
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
    


