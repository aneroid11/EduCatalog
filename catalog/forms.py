from django import forms
from django.core.exceptions import ValidationError


class RenewBookForm(forms.Form):
    user_search = forms.CharField(help_text="Введите ключевое слово или фразу")

    def clean_user_search(self):
        data = self.cleaned_data['user_search']

        # check something here...
        # if data < datetime.date.today():
        #    raise ValidationError(_('Invalid date - renewal in past'))
        return data
