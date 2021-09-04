from datetime import timedelta
from json import loads as json_decode, dumps as json_encode

from django.test import TestCase
from django.urls import reverse

from ..libs.factories import fake
from .models import Account, Token


class CustomTestCase(TestCase):
    def __str__(self):
        # Print test case names in the format that the command line expects.
        return "%s.%s.%s" % (self.__class__.__module__, self.__class__.__name__, self._testMethodName)
    
    def setUp(self):
        from django.utils import timezone
        super().setUp()
        self.started = timezone.now()
    
    def assertTimestamped(self, when, delta=timedelta()):
        from django.utils import timezone
        self.assertIsNotNone(when)
        self.assertLessEqual(self.started + delta, when)
        self.assertLessEqual(when, timezone.now() + delta)
    
    def assertJsonResponse(self, response, status_code=200):
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertEqual(response.content[0], b'{'[0])
        return json_decode(response.content).get('result')
    
    def assertCreated(self, model, code, **fields):
        self.assertIsInstance(code, str)
        item = model.objects.get(code=code)
        self.assertTimestamped(item.created)
        self.assertTimestamped(item.modified)
        self.assertIsNone(item.deleted)
        for field, value in fields.items():
            self.assertEqual(getattr(item, field), value)
        return item


class AccountTests(CustomTestCase):
    def test_create(self):
        # Posting to the account list should create an account, with a new token.
        name = fake.company()
        data = {'name': name}
        response = self.client.post(reverse('accounts'), data=data)
        result = self.assertJsonResponse(response)
        
        account = self.assertCreated(Account, result.get('account', {}).get('id'), name=name)
        self.assertEqual(result['account'].get('name'), name)
        
        token = self.assertCreated(Token, result.get('token', {}).get('id'), account_id=account.id)
        self.assertEqual(result['token'].get('account'), account.code)
        self.assertEqual(result['token'].get('uuid'), str(token.uuid))
    
    def test_create_json(self):
        # Posting as JSON should also work.
        name = fake.company()
        data = json_encode({'name': name})
        response = self.client.post(reverse('accounts'), data, content_type='application/json')
        result = self.assertJsonResponse(response)
        account = self.assertCreated(Account, result.get('account', {}).get('id'), name=name)
