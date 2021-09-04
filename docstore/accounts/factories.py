from django.utils import timezone
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker as FakeAttribute


class AccountFactory(DjangoModelFactory):
    class Meta:
        model = 'accounts.Account'
    
    name = FakeAttribute('company')
    created = FakeAttribute('date_time_this_month', before_now=True, tzinfo=timezone.utc)
    modified = FakeAttribute('date_time_this_month', before_now=True, tzinfo=timezone.utc)


class TokenFactory(DjangoModelFactory):
    class Meta:
        model = 'accounts.Token'
    
    account = SubFactory(AccountFactory)
    uuid = FakeAttribute('uuid4')
    created = FakeAttribute('date_time_this_month', before_now=True, tzinfo=timezone.utc)
    modified = FakeAttribute('date_time_this_month', before_now=True, tzinfo=timezone.utc)
