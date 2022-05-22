import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Введите дату от сегодняшнего дня до 4-х недель (по умолчанию 3 недели)",
                                   label="Дата возврата")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        if data < datetime.date.today():
            raise ValidationError(gettext_lazy("Дата не должна быть в прошлом"))
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(gettext_lazy("Дата не должна быть дальше, чем 4 недели"))

        return data
