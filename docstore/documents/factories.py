from django.utils import timezone
from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker as FakeAttribute

from ..accounts.factories import AccountFactory


class DocumentFactory(DjangoModelFactory):
    class Meta:
        model = 'documents.Document'
    
    account = SubFactory(AccountFactory)
    name = FakeAttribute('catch_phrase')
    content = FakeAttribute('text')
    created = FakeAttribute('date_time_this_month', before_now=True, tzinfo=timezone.utc)
    modified = FakeAttribute('date_time_this_month', before_now=True, tzinfo=timezone.utc)
