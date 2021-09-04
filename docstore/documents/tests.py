from uuid import uuid4
from json import dumps as json_encode

from django.urls import reverse

from ..libs.factories import fake
from ..libs.tests import CustomTestCase
from ..accounts.factories import TokenFactory
from .models import Document


class DocumentCreationTests(CustomTestCase):
    def test_create(self):
        token = TokenFactory()
        data = {
            'name': fake.bs(),
            'content': "\n".join(fake.paragraphs()),
        }
        response = self.post_json('documents', data, token=token.uuid)
        result = self.assertJsonResponse(response)
        
        account_code = result.get('document', {}).get('id')
        account = self.assertCreated(Document, account_code, account_id=token.account_id, **data)
        self.assertEqual(result['document'].get('name'), data['name'])
        self.assertEqual(result['document'].get('content'), data['content'])
        self.assertEqual(result['document'].get('account'), token.account.code)
    
    def test_requires_token(self):
        # Document creation should require a valid account token.
        documents = Document.objects.all().count()
        token = TokenFactory()
        data = {
            'name': fake.bs(),
            'content': "\n".join(fake.paragraphs()),
        }
        
        with self.subTest("Without an authorization token"):
            path = reverse('documents')
            payload = json_encode(data)
            response = self.client.post(path, payload, content_type='application/json')
            result = self.assertJsonResponse(response, status_code=401)
            self.assertEqual(result, None)
            self.assertEqual(Document.objects.all().count(), documents)
        
        with self.subTest("With an incorrect authorization token"):
            response = self.post_json('documents', data, token=uuid4())
            result = self.assertJsonResponse(response, status_code=401)
            self.assertEqual(result, None)
            self.assertEqual(Document.objects.all().count(), documents)
        
        with self.subTest("With an invalid authorization token"):
            response = self.post_json('documents', data, token=fake.word())
            result = self.assertJsonResponse(response, status_code=401)
            self.assertEqual(result, None)
            self.assertEqual(Document.objects.all().count(), documents)
