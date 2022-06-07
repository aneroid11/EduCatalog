from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from creditcards.forms import CardNumberField, CardExpiryField, SecurityCodeField


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")


class GetUserCardDataForm(forms.Form):
    card_number = CardNumberField(label="Card number field")
    card_expiry = CardExpiryField(label='Expiration Date')
    card_code = SecurityCodeField(label='CVV/CVC')
