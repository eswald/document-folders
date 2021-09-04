from datetime import datetime, timedelta
from json import loads as json_decode, dumps as json_encode

from dateutil.parser import parse as parse_datetime
from django.test import TestCase
from django.utils import timezone


class Timestamp(object):
    def __init__(self, expected, delta=timedelta(seconds=1)):
        self.expected = expected
        self.delta = delta
    
    def __eq__(self, other):
        if isinstance(other, Timestamp):
            return (
                self.expected == other.expected
                and self.delta == other.delta
            )
        item = self.parse_timestamp(other)
        if item == self.expected:
            return True
        if self.delta is not None:
            try:
                if abs(item - self.expected) < self.delta:
                    # Close enough.
                    return True
            except TypeError:
                # Not even comparable.
                return False
        return False
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.expected}, {self.delta})'
    
    @staticmethod
    def parse_timestamp(value):
        """Parses a timestamp from numeric or string format into an aware datetime instance."""
        if value is None:
            return None
        try:
            number = decimal.Decimal(value)
        except Exception:
            pass
        else:
            if number > 1e10:
                number /= 1000
            return timezone.make_aware(datetime.utcfromtimestamp(number), timezone.utc)
        return parse_datetime(value)


class CustomTestCase(TestCase):
    maxDiff = 5000
    
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
    
    def call_api(self, method, path, data=None, token=None):
        return self.client.generic(
            method = method,
            path = path,
            data = json_encode(data),
            content_type = 'application/json',
            HTTP_AUTHORIZATION = f"Bearer {token}",
        )
