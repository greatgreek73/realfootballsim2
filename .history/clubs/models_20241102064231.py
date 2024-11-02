from django.db import models
from django.conf import settings
from django_countries.fields import CountryField
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class Club(models.Model):
    name = models.CharField(max_length=100, verbose_name="Club Name")
    country = CountryField(blank_label='(select country)', verbose_name="Country")
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="Owner", 
        related_name="club",
        null=True,
        blank=True
    )
    lineup = models.JSONField(null=True, blank=True)
    is_bot = models.BooleanField(
        default=False,
        verbose_name="Bot Team",
        help_text="Indicates if this team is controlled by AI"
    )

    def __str__(self):
        return self.name

    def clean(self):
        logger.debug(f"Clean method called for club {self.name}")
        
        # Пропускаем валидацию если установлен флаг
        if hasattr(self, '_skip_clean'):
            logger.debug("Skipping validation due to _skip_clean flag")
            return
        
        logger.debug(f"Current attributes - is_bot: {self.is_bot}, owner: {self.owner}")
        
        if not self.is_bot and not self.owner:
            logger.warning(f"Validation failed for club {self.name} - no owner set")
            raise ValidationError("Non-bot teams must have an owner")
        
        logger.debug(f"Clean method completed successfully for club {self.name}")

    def save(self, *args, **kwargs):
        logger.debug(f"Save method called for club {self.name}")
        logger.debug(f"Save attributes - is_bot: {self.is_bot}, owner: {self.owner}")
        
        # Пропускаем валидацию если установлен флаг
        if not hasattr(self, '_skip_clean'):
            self.full_clean()
            
        super().save(*args, **kwargs)
        logger.debug(f"Save completed for club {self.name}")