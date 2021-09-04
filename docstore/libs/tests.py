from datetime import timedelta
from json import loads as json_decode, dumps as json_encode

from django.test import TestCase
from django.urls import reverse


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
    
    def post_json(self, view_name, data, token):
        return self.client.post(
            path = reverse(view_name),
            data = json_encode(data),
            content_type = 'application/json',
            HTTP_AUTHORIZATION = f"Bearer {token}",
        )
