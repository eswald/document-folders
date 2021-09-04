from django.forms import ModelForm, CharField

from .models import Account


class AccountRegistrationForm(ModelForm):
    name = CharField(max_length=127, required=True)

    class Meta:
        model = Account
        fields = [
            'name',
        ]
