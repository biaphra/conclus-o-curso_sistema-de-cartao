from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Card


class CardForm(forms.ModelForm):
    holder_name = forms.CharField(
        label="Nome impresso no cartão",
        min_length=3,
        max_length=20,
        help_text="Digite seu nome como deseja que apareça no cartão.",
    )

    def clean_holder_name(self):
        name = " ".join(self.cleaned_data["holder_name"].split()).upper()
        if not all(character.isalpha() or character in " '-" for character in name):
            raise forms.ValidationError("Use apenas letras, espaços, apóstrofo ou hífen.")
        return name

    class Meta:
        model = Card
        fields = ["holder_name"]


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="E-mail", required=True)
    first_name = forms.CharField(label="Nome", max_length=150, required=True)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("first_name", "username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if get_user_model().objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email
