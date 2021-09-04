from django.conf import settings
from django.db.models import DateTimeField, Expression, Manager, Model, QuerySet
from django.utils import timezone

from .functional import cached_class_property
from .idencoder import encode, decode


class BasicQuerySet(QuerySet):
    def collect(self, aggregation, default=None):
        result = self.aggregate(result=aggregation)['result']
        if result is None:
            return default
        return result
    
    def field(self, field, *args, **kwargs):
        r'''Collect a single field value from a single row.
        '''#"""#'''
        
        return self.value_list(field).get(*args, **kwargs)
    
    def filter(self, *args, **kwargs):
        if 'code' in kwargs:
            kwargs['id'] = self.model.decode(kwargs.pop('code', -1))
        if 'code__in' in kwargs:
            codes = []
            for code in kwargs.pop('code__in'):
                codes.append(self.model.decode(code, -1))
                kwargs['id__in'] = codes
        return super().filter(*args, **kwargs)
    
    def vals(self, field):
        return self.values_list(field, flat=True)
    
    def value_list(self, field):
        return self.values_list(field, flat=True)


class BasicManager(Manager):
    def encode(self, val):
        return self.model.encode(val)

    def decode(self, code):
        return self.model.decode(code)
BasicQuerySetManager = BasicManager.from_queryset(BasicQuerySet)


class SoftDeleteManager(BasicManager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=None)
SoftDeleteQuerySetManager = SoftDeleteManager.from_queryset(BasicQuerySet)


class BasicModel(Model):
    # Record creation and modification timestamps.
    created = DateTimeField(default=timezone.now, editable=False)
    modified = DateTimeField(auto_now=True, editable=False)
    deleted = DateTimeField(null=True, default=None, blank=True, editable=False)
    
    # Hide deleted rows by default.
    objects = SoftDeleteQuerySetManager()
    all_objects = BasicQuerySetManager()

    class Meta:
        abstract = True

    @cached_class_property
    def alphabet(cls):
        return settings.ENCODER_ALPHABETS[cls.__name__]

    @cached_class_property
    def code_prefix(cls):
        r'''A string to be prepended to identifier codes for this model.
            Identifier codes that don't start with this string will be rejected.
            Can be overridden by simply setting `code_prefix` on a subclass.
            By default, it's based on the capital letter(s) of the model name.
        '''#"""#'''
        return ''.join(c.lower() for c in cls.__name__ if c.isupper()) + '-'

    @property
    def code(self):
        return self.__class__.encode(self.pk) if self.pk else None
    
    @classmethod
    def decode(cls, code, default=None):
        if not isinstance(code, str):
            return default
        prefix = cls.code_prefix
        val = decode(code[len(prefix):], cls.alphabet, default)
        if not code.startswith(prefix):
            return default
        return val
    
    @classmethod
    def encode(cls, val):
        return cls.code_prefix + encode(val, cls.alphabet)
    
    def __str__(self):
        return '%s #%s (%s)' % (self.__class__.__name__, self.pk, self.code)
    
    def delete(self):
        self.update(deleted=timezone.now())
    delete.alters_data = True

    def update(self, **kwargs):
        r'''Update field values both on the instance and in the database.
            Safer than .save() without parameters, because it doesn't
            accidentally overwrite changes in other fields.
        '''#"""#'''
        
        expressions = set()
        for field in kwargs:
            setattr(self, field, kwargs[field])
            if isinstance(kwargs[field], Expression):
                # Handle things like F(field) + 1, for example.
                expressions.add(field)
        self.save(update_fields=list(kwargs))
        if expressions:
            # Retrieve the actual values of any calculated fields.
            values = self.__class__._base_manager.values(*expressions).get(pk=self.pk)
            for field in values:
                setattr(self, field, values[field])
    update.alters_data = True

    def fast_update(self, **kwargs):
        r'''Update field values in the database, but not on the instance.
            This avoids a second query when Expressions are used,
            and skips any signal processing or custom save() logic.
        '''#"""#'''

        objects = self.__class__._base_manager
        return objects.filter(pk=self.pk).update(**kwargs)
    fast_update.alters_data = True
    
    def get_admin_url(self):
        from django.urls import reverse
        return reverse("admin:%s_%s_change" % (self._meta.app_label, self._meta.model_name), args=(self.id,))
