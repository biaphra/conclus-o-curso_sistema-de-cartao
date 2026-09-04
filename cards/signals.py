from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Card, StatusHistory


@receiver(pre_save, sender=Card)
def remember_previous_status(sender, instance, **kwargs):
    instance._previous_status = None
    if instance.pk:
        instance._previous_status = sender.objects.filter(pk=instance.pk).values_list("status", flat=True).first()


@receiver(post_save, sender=Card)
def record_and_notify_status(sender, instance, created, **kwargs):
    changed = created or instance._previous_status != instance.status
    if not changed:
        return
    StatusHistory.objects.create(card=instance, status=instance.status)
    if not created and instance.user.email:
        send_mail(
            "Atualização da sua solicitação de cartão",
            f"Olá, {instance.user.get_short_name() or instance.user.username}. O status do cartão final {instance.last_four} agora é {instance.get_status_display()}.",
            settings.DEFAULT_FROM_EMAIL,
            [instance.user.email],
            fail_silently=True,
        )
