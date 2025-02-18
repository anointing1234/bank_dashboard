from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import AccountBalance

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_account_balance(sender, instance, created, **kwargs):
    if created:
        AccountBalance.objects.create(account=instance)






        