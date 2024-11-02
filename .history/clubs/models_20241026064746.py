from django.db import models
from django.conf import settings
from django_countries.fields import CountryField

class Club(models.Model):
    name = models.CharField(max_length=100, verbose_name="Club Name")
    country = CountryField(blank_label='(select country)', verbose_name="Country")
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Owner", related_name="club")
    lineup = models.JSONField(null=True, blank=True)

    is_bot = models.BooleanField(
    default=False,
    verbose_name="Bot Team",
    help_text="Indicates if this team is controlled by AI"
    )


    def __str__(self):
        return self.name
