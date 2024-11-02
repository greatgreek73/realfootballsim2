from django import forms
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
            'country': forms.Select(attrs={
                'class': 'form-control'
            })
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Пропускаем валидацию при первом сохранении
        instance._skip_validation = True
        if commit:
            instance.save()
        return instance