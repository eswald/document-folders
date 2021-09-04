from uuid import uuid4
from json import dumps as json_encode

from django.urls import reverse
from django.utils import timezone
from factory.faker import Faker as FakeAttribute

from ..libs.factories import ListFactory, fake
from ..libs.tests import CustomTestCase, Timestamp
from ..accounts.factories import TokenFactory
from .factories import DocumentFactory
from .models import Document


class DocumentCreationTests(CustomTestCase):
    def test_create(self):
        token = TokenFactory()
        data = {
            'name': fake.bs(),
            'content': "\n".join(fake.paragraphs()),
        }
        response = self.call_api('POST', 'documents', data, token=token.uuid)
        result = self.assertJsonResponse(response)
        
        account_code = result.get('document', {}).get('id')
        document = self.assertCreated(Document, account_code, account_id=token.account_id, **data)
        
        self.assertEqual(result, {'document': {
            'id': document.code,
            'name': data['name'],
            'content': data['content'],
            'account': token.account.code,
            'created': Timestamp(document.created),
            'modified': Timestamp(document.modified),
            'deleted': None,
        }})
    
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
            response = self.call_api('POST', 'documents', data, token=uuid4())
            result = self.assertJsonResponse(response, status_code=401)
            self.assertEqual(result, None)
            self.assertEqual(Document.objects.all().count(), documents)
        
        with self.subTest("With an invalid authorization token"):
            response = self.call_api('POST', 'documents', data, token=fake.word())
            result = self.assertJsonResponse(response, status_code=401)
            self.assertEqual(result, None)
            self.assertEqual(Document.objects.all().count(), documents)


class DocumentListTests(CustomTestCase):
    def test_list(self):
        token = TokenFactory()
        documents = ListFactory(DocumentFactory, account=token.account)
        response = self.call_api('GET', 'documents', token=token.uuid)
        result = self.assertJsonResponse(response)
        
        expected = [{
            'id': document.code,
            'name': document.name,
            'content': document.content,
            'account': token.account.code,
            'created': Timestamp(document.created),
            'modified': Timestamp(document.modified),
            'deleted': None,
        } for document in documents]
        
        self.assertCountEqual(result.get('documents'), expected)
        self.assertEqual(Document.objects.all().count(), len(documents))
    
    def test_queries(self):
        # The number of queries should not depend on the number of documents.
        token = TokenFactory()
        documents = ListFactory(DocumentFactory, account=token.account)
        with self.assertNumQueries(2):
            response = self.call_api('GET', 'documents', token=token.uuid)
    
    def test_foreign(self):
        # The returned documents should not include documents of other accounts.
        token = TokenFactory()
        documents = ListFactory(DocumentFactory, account=token.account)
        foreign = ListFactory(DocumentFactory)
        response = self.call_api('GET', 'documents', token=token.uuid)
        result = self.assertJsonResponse(response)
        collected = [doc['id'] for doc in result['documents']]
        self.assertCountEqual(collected, [doc.code for doc in documents])
    
    def test_deleted(self):
        # The returned documents should not include deleted documents.
        token = TokenFactory()
        documents = ListFactory(DocumentFactory, account=token.account)
        recent = FakeAttribute('date_time_this_month', before_now=True, tzinfo=timezone.utc)
        foreign = ListFactory(DocumentFactory, account=token.account, deleted=recent)
        response = self.call_api('GET', 'documents', token=token.uuid)
        result = self.assertJsonResponse(response)
        collected = [doc['id'] for doc in result['documents']]
        self.assertCountEqual(collected, [doc.code for doc in documents])
