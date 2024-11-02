from django import forms
from .models import Club
import logging

logger = logging.getLogger(__name__)

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

    def save(self, commit=True, user=None):
        logger.debug("ClubForm save method called")
        logger.debug(f"Commit: {commit}, User: {user}")
        
        instance = super().save(commit=False)
        logger.debug(f"Instance created with name: {instance.name}")
        
        if user:
            logger.debug(f"Setting owner to user: {user.username}")
            instance.owner = user
            instance.is_bot = False
            logger.debug("Owner and is_bot fields set")
        
        if commit:
            logger.debug("Attempting to save instance")
            try:
                instance.save()
                logger.debug("Instance saved successfully")
            except Exception as e:
                logger.error(f"Error saving instance: {str(e)}")
                raise
        
        return instance