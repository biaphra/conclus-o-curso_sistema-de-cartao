from django.contrib.auth.models import User
from django.db import models


class Card(models.Model):
    STATUS_CHOICES = (
        ("P", "Pendente"),
        ("A", "Aprovado"),
        ("E", "Enviado"),
        ("R", "Recebido"),
    )

    CARD_NETWORK = (
        ("V", "Visa"),
        ("M", "Mastercard"),
    )

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="cards", verbose_name="Usuário")
    name = models.CharField("Nome", max_length=20)
    token = models.CharField("Token", max_length=64, unique=True, editable=False)
    last_four = models.CharField("Últimos quatro dígitos", max_length=4, editable=False)
    holder_name = models.CharField("Titular", max_length=20)
    network = models.CharField("Rede", max_length=1, choices=CARD_NETWORK)
    expiration_date = models.CharField("Data de expiração", max_length=5)
    status = models.CharField("Status", max_length=1, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0])
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Alterado em", auto_now=True)

    def __str__(self) -> str:
        return f"Cartão {self.id} - {self.user.username} - {self.get_status_display()}"

    @property
    def masked_number(self) -> str:
        return f"•••• •••• •••• {self.last_four}"

    class Meta:
        verbose_name_plural = "Cartões"
        ordering = ["-created_at"]


class StatusHistory(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="history", verbose_name="Cartão")
    status = models.CharField("Status", max_length=1, choices=Card.STATUS_CHOICES)
    created_at = models.DateTimeField("Registrado em", auto_now_add=True)

    class Meta:
        verbose_name = "Histórico de status"
        verbose_name_plural = "Históricos de status"
        ordering = ["-created_at"]
