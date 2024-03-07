import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def generate_uuid_and_update_username(sender, instance, created, **kwargs):
    if created and not instance.username:
        uuid_str = str(uuid.uuid4()).replace("-", "")

        role = instance.role.upper()
        if role in ["CLIENT", "CODER", "COWORKER", "SUCCESS-MANAGER"]:
            prefix = role.lower()
        else:
            prefix = "user"

        instance.username = f"{prefix}_{uuid_str}"
        instance.save()
