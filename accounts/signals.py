from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_initial_tokens(sender, instance, created, **kwargs):
    if created:
        instance.tokens = 3000
        instance.save()