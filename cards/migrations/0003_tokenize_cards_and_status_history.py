import secrets

import django.db.models.deletion
from django.db import migrations, models


def tokenize_existing_cards(apps, schema_editor):
    Card = apps.get_model("cards", "Card")
    for card in Card.objects.all().iterator():
        card.last_four = card.number[-4:]
        card.token = secrets.token_urlsafe(32)
        card.save(update_fields=["last_four", "token"])


def create_initial_history(apps, schema_editor):
    Card = apps.get_model("cards", "Card")
    StatusHistory = apps.get_model("cards", "StatusHistory")
    StatusHistory.objects.bulk_create(StatusHistory(card=card, status=card.status) for card in Card.objects.all())


class Migration(migrations.Migration):
    dependencies = [("cards", "0002_alter_card_options_alter_card_created_at_and_more")]

    operations = [
        migrations.AddField(model_name="card", name="last_four", field=models.CharField(editable=False, max_length=4, null=True, verbose_name="Últimos quatro dígitos")),
        migrations.AddField(model_name="card", name="token", field=models.CharField(editable=False, max_length=64, null=True, verbose_name="Token")),
        migrations.RunPython(tokenize_existing_cards, migrations.RunPython.noop),
        migrations.AlterField(model_name="card", name="last_four", field=models.CharField(editable=False, max_length=4, verbose_name="Últimos quatro dígitos")),
        migrations.AlterField(model_name="card", name="token", field=models.CharField(editable=False, max_length=64, unique=True, verbose_name="Token")),
        migrations.RemoveField(model_name="card", name="cvv"),
        migrations.RemoveField(model_name="card", name="number"),
        migrations.CreateModel(
            name="StatusHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("P", "Pendente"), ("A", "Aprovado"), ("E", "Enviado"), ("R", "Recebido")], max_length=1, verbose_name="Status")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Registrado em")),
                ("card", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="history", to="cards.card", verbose_name="Cartão")),
            ],
            options={"verbose_name": "Histórico de status", "verbose_name_plural": "Históricos de status", "ordering": ["-created_at"]},
        ),
        migrations.RunPython(create_initial_history, migrations.RunPython.noop),
    ]
