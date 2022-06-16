"""Catalog forms."""

from creditcards.forms import (CardExpiryField, CardNumberField,
                               SecurityCodeField)
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegisterForm(UserCreationForm):
    """The form to register a user account."""

    class Meta:
        """Meta info."""

        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")


class GetUserCardDataForm(forms.Form):
    """The form to get credit card data from user."""

    card_number = CardNumberField(label="Card number field")
    card_expiry = CardExpiryField(label='Expiration Date')
    card_code = SecurityCodeField(label='CVV/CVC')
