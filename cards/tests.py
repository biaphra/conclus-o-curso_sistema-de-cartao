from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import CardForm
from .models import Card, StatusHistory
from .services import calculate_luhn_digit, generate_card_data


class CardFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="cliente", password="senha-forte-123")
        self.other_user = get_user_model().objects.create_user(username="outro", password="senha-forte-123")

    def test_private_pages_require_login(self):
        response = self.client.get(reverse("cards:view_requests"))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('cards:view_requests')}")

    def test_user_can_request_card(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("cards:request_card"), {"holder_name": "  Maria da Silva  "})

        self.assertRedirects(response, reverse("cards:view_requests"))
        card = Card.objects.get(user=self.user)
        self.assertEqual(card.holder_name, "MARIA DA SILVA")
        self.assertEqual(len(card.last_four), 4)
        self.assertGreaterEqual(len(card.token), 32)
        self.assertEqual(StatusHistory.objects.filter(card=card, status="P").count(), 1)

    def test_user_cannot_view_another_users_card(self):
        card = Card.objects.create(
            user=self.other_user,
            name="DIO Bank Platinum",
            token="token-other-user",
            last_four="3456",
            holder_name="OUTRO CLIENTE",
            network="V",
            expiration_date="01/36",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("cards:card_details", args=[card.id]))
        self.assertEqual(response.status_code, 404)

    def test_details_mask_sensitive_values(self):
        card = Card.objects.create(
            user=self.user,
            name="DIO Bank Platinum",
            token="token-current-user",
            last_four="3456",
            holder_name="MARIA SILVA",
            network="M",
            expiration_date="01/36",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("cards:card_details", args=[card.id]))
        self.assertContains(response, "3456")
        self.assertNotContains(response, "1234567890123456")
        self.assertNotContains(response, "123</")

    def test_api_only_returns_safe_fields(self):
        Card.objects.create(user=self.user, name="DIO Bank Platinum", token="safe-token", last_four="9876", holder_name="MARIA", network="V", expiration_date="01/36")
        self.client.force_login(self.user)
        response = self.client.get(reverse("cards:api"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"][0]["last_four"], "9876")
        self.assertNotIn("token", response.json()["results"][0])

    def test_status_change_creates_history_and_email(self):
        card = Card.objects.create(user=self.user, name="DIO Bank Platinum", token="status-token", last_four="1111", holder_name="MARIA", network="V", expiration_date="01/36")
        card.status = "A"
        card.save()
        self.assertEqual(StatusHistory.objects.filter(card=card).count(), 2)


class CardFormTests(TestCase):
    def test_rejects_invalid_holder_name(self):
        form = CardForm({"holder_name": "Maria 123"})
        self.assertFalse(form.is_valid())

    def test_normalizes_holder_name(self):
        form = CardForm({"holder_name": "  Ana   d'Ávila "})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["holder_name"], "ANA D'ÁVILA")


class CardGenerationTests(TestCase):
    def test_generated_number_uses_luhn_before_tokenization(self):
        data = generate_card_data()
        self.assertEqual(len(data["last_four"]), 4)
        self.assertNotIn("number", data)
        self.assertNotIn("cvv", data)

    def test_luhn_check_digit(self):
        self.assertEqual(calculate_luhn_digit("7992739871"), "3")


class AccountTests(TestCase):
    def test_signup_creates_and_logs_user_in(self):
        response = self.client.post(reverse("signup"), {"first_name": "Ana", "username": "ana", "email": "ana@example.com", "password1": "uma-senha-forte-4829", "password2": "uma-senha-forte-4829"})
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(get_user_model().objects.filter(username="ana").exists())
