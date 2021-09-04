from json import dumps as json_encode

from ..libs.factories import fake
from ..libs.tests import CustomTestCase
from .models import Account, Token


class AccountTests(CustomTestCase):
    def test_create(self):
        # Posting to the account list should create an account, with a new token.
        name = fake.company()
        data = {'name': name}
        response = self.client.post('/accounts/', data=data)
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
        response = self.client.post('/accounts/', data, content_type='application/json')
        result = self.assertJsonResponse(response)
        account = self.assertCreated(Account, result.get('account', {}).get('id'), name=name)
